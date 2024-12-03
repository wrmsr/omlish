"""
https:#github.com/avinassh/s3-log
"""
# MIT License
#
# Copyright (c) 2024 Avinash Sajjanshetty <opensource@avi.im>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
type Record struct {
    Offset uint64
    Data   []byte
}

type WAL interface {
    Append(ctx context.Context, data []byte) (uint64, error)
    Read(ctx context.Context, offset uint64) (Record, error)
    LastRecord(ctx context.Context) (Record, error)
}

##

type S3WAL struct {
    client     *s3.Client
    bucketName string
    prefix     string
    length     uint64
}

func NewS3WAL(client *s3.Client, bucketName, prefix string) *S3WAL {
    return &S3WAL{
        client:     client,
        bucketName: bucketName,
        prefix:     prefix,
        length:     0,
    }
}

func (w *S3WAL) getObjectKey(offset uint64) string {
    return w.prefix + "/" + fmt.Sprintf("%020d", offset)
}

func (w *S3WAL) getOffsetFromKey(key string) (uint64, error) {
    # skip the `w.prefix` and "/"
    numStr := key[len(w.prefix)+1:]
    return strconv.ParseUint(numStr, 10, 64)
}

func calculateChecksum(buf *bytes.Buffer) [32]byte {
    return sha256.Sum256(buf.Bytes())
}

func validateChecksum(data []byte) bool {
    var storedChecksum [32]byte
    copy(storedChecksum[:], data[len(data)-32:])
    recordData := data[:len(data)-32]
    return storedChecksum == calculateChecksum(bytes.NewBuffer(recordData))
}

func prepareBody(offset uint64, data []byte) ([]byte, error) {
    # 8 bytes for offset, len(data) bytes for data, 32 bytes for checksum
    bufferLen := 8 + len(data) + 32
    buf := bytes.NewBuffer(make([]byte, 0, bufferLen))
    if err := binary.Write(buf, binary.BigEndian, offset); err != nil {
        return nil, err
    }
    if _, err := buf.Write(data); err != nil {
        return nil, err
    }
    checksum := calculateChecksum(buf)
    _, err := buf.Write(checksum[:])
    return buf.Bytes(), err
}

func (w *S3WAL) Append(ctx context.Context, data []byte) (uint64, error) {
    nextOffset := w.length + 1

    buf, err := prepareBody(nextOffset, data)
    if err != nil {
        return 0, fmt.Errorf("failed to prepare object body: %w", err)
    }

    input := &s3.PutObjectInput{
        Bucket:      aws.String(w.bucketName),
        Key:         aws.String(w.getObjectKey(nextOffset)),
        Body:        bytes.NewReader(buf),
        IfNoneMatch: aws.String("*"),
    }

    if _, err = w.client.PutObject(ctx, input); err != nil {
        return 0, fmt.Errorf("failed to put object to S3: %w", err)
    }
    w.length = nextOffset
    return nextOffset, nil
}

func (w *S3WAL) Read(ctx context.Context, offset uint64) (Record, error) {
    key := w.getObjectKey(offset)
    input := &s3.GetObjectInput{
        Bucket: aws.String(w.bucketName),
        Key:    aws.String(key),
    }

    result, err := w.client.GetObject(ctx, input)
    if err != nil {
        return Record{}, fmt.Errorf("failed to get object from S3: %w", err)
    }
    defer result.Body.Close()

    data, err := io.ReadAll(result.Body)
    if err != nil {
        return Record{}, fmt.Errorf("failed to read object body: %w", err)
    }
    if len(data) < 40 {
        return Record{}, fmt.Errorf("invalid record: data too short")
    }

    var storedOffset uint64
    if err = binary.Read(bytes.NewReader(data[:8]), binary.BigEndian, &storedOffset); err != nil {
        return Record{}, err
    }
    if storedOffset != offset {
        return Record{}, fmt.Errorf("offset mismatch: expected %d, got %d", offset, storedOffset)
    }
    if !validateChecksum(data) {
        return Record{}, fmt.Errorf("checksum mismatch")
    }
    return Record{
        Offset: storedOffset,
        Data:   data[8 : len(data)-32],
    }, nil
}

func (w *S3WAL) LastRecord(ctx context.Context) (Record, error) {
    input := &s3.ListObjectsV2Input{
        Bucket: aws.String(w.bucketName),
        Prefix: aws.String(w.prefix + "/"),
    }
    paginator := s3.NewListObjectsV2Paginator(w.client, input)

    var maxOffset uint64 = 0
    for paginator.HasMorePages() {
        output, err := paginator.NextPage(ctx)
        if err != nil {
            return Record{}, fmt.Errorf("failed to list objects from S3: %w", err)
        }
        for _, obj := range output.Contents {
            key := *obj.Key
            offset, err := w.getOffsetFromKey(key)
            if err != nil {
                return Record{}, fmt.Errorf("failed to parse offset from key: %w", err)
            }
            if offset > maxOffset {
                maxOffset = offset
            }
        }
    }
    if maxOffset == 0 {
        return Record{}, fmt.Errorf("WAL is empty")
    }
    w.length = maxOffset
    return w.Read(ctx, maxOffset)
}

##

func generateRandomStr() string {
    b := make([]byte, 8)
    rand.Read(b)
    return hex.EncodeToString(b)
}

func setupMinioClient() *s3.Client {
    # https:#stackoverflow.com/a/78815403
    # thank you lurenyang
    return s3.NewFromConfig(aws.Config{Region: "us-east-1"}, func(o *s3.Options) {
        o.BaseEndpoint = aws.String("http:#127.0.0.1:9000")
        o.Credentials = credentials.NewStaticCredentialsProvider("minioadmin", "minioadmin", "")
    })
}

func setupBucket(client *s3.Client, bucketName string) error {
    _, err := client.CreateBucket(context.Background(), &s3.CreateBucketInput{
        Bucket: aws.String(bucketName),
    })
    # if the bucket already exists, ignore the error
    var bae *types.BucketAlreadyExists
    var boe *types.BucketAlreadyOwnedByYou
    if err != nil && !errors.As(err, &bae) && !errors.As(err, &boe) {
        return err
    }
    return nil
}

# emptyBucket deletes the bucket because dumbass AWS does not have a direct API
func emptyBucket(ctx context.Context, client *s3.Client, bucketName, prefix string) error {
    input := &s3.ListObjectsV2Input{
        Bucket: aws.String(bucketName),
        Prefix: aws.String(prefix),
    }
    paginator := s3.NewListObjectsV2Paginator(client, input)
    for paginator.HasMorePages() {
        output, err := paginator.NextPage(ctx)
        if err != nil {
            return fmt.Errorf("failed to list objects: %w", err)
        }
        if len(output.Contents) == 0 {
            continue
        }
        objectIds := make([]types.ObjectIdentifier, len(output.Contents))
        for i, object := range output.Contents {
            objectIds[i] = types.ObjectIdentifier{
                Key: object.Key,
            }
        }
        deleteInput := &s3.DeleteObjectsInput{
            Bucket: aws.String(bucketName),
            Delete: &types.Delete{
                Objects: objectIds,
                Quiet:   aws.Bool(false),
            },
        }
        _, err = client.DeleteObjects(ctx, deleteInput)
        if err != nil {
            return fmt.Errorf("failed to delete objects: %w", err)
        }
    }

    return nil
}

func getWAL(t *testing.T) (*S3WAL, func()) {
    client := setupMinioClient()
    bucketName := "test-wal-bucket-" + generateRandomStr()
    prefix := generateRandomStr()

    if err := setupBucket(client, bucketName); err != nil {
        t.Fatal(err)
    }
    cleanup := func() {
        if err := emptyBucket(context.Background(), client, bucketName, prefix); err != nil {
            t.Logf("failed to empty bucket during cleanup: %v", err)
        }
        _, err := client.DeleteBucket(context.Background(), &s3.DeleteBucketInput{
            Bucket: aws.String(bucketName),
        })
        if err != nil {
            t.Logf("failed to delete bucket during cleanup: %v", err)
        }
    }
    return NewS3WAL(client, bucketName, prefix), cleanup
}

func TestAppendAndReadSingle(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()
    testData := []byte("hello world")

    offset, err := wal.Append(ctx, testData)
    if err != nil {
        t.Fatalf("failed to append: %v", err)
    }

    if offset != 1 {
        t.Errorf("expected first offset to be 1, got %d", offset)
    }

    record, err := wal.Read(ctx, offset)
    if err != nil {
        t.Fatalf("failed to read: %v", err)
    }

    if record.Offset != offset {
        t.Errorf("offset mismatch: expected %d, got %d", offset, record.Offset)
    }

    if string(record.Data) != string(testData) {
        t.Errorf("data mismatch: expected %q, got %q", testData, record.Data)
    }
}

func TestAppendMultiple(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()

    testData := [][]byte{
        []byte("Do not answer. Do not answer. Do not answer."),
        []byte("I am a pacifist in this world. You are lucky that I am first to receive your message."),
        []byte("I am warning you: do not answer. If you respond, we will come. Your world will be conquered"),
        []byte("Do not answer."),
    }

    var offsets []uint64
    for _, data := range testData {
        offset, err := wal.Append(ctx, data)
        if err != nil {
            t.Fatalf("failed to append: %v", err)
        }
        offsets = append(offsets, offset)
    }

    for i, offset := range offsets {
        record, err := wal.Read(ctx, offset)
        if err != nil {
            t.Fatalf("failed to read offset %d: %v", offset, err)
        }

        if record.Offset != offset {
            t.Errorf("offset mismatch: expected %d, got %d", offset, record.Offset)
        }

        if string(record.Data) != string(testData[i]) {
            t.Errorf("data mismatch at offset %d: expected %q, got %q",
                offset, testData[i], record.Data)
        }
    }
}

func TestReadNonExistent(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    _, err := wal.Read(context.Background(), 99999)
    if err == nil {
        t.Error("expected error when reading non-existent record, got nil")
    }
}

func TestAppendEmpty(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()

    offset, err := wal.Append(ctx, []byte{})
    if err != nil {
        t.Fatalf("failed to append empty data: %v", err)
    }

    record, err := wal.Read(ctx, offset)
    if err != nil {
        t.Fatalf("failed to read empty record: %v", err)
    }

    if len(record.Data) != 0 {
        t.Errorf("expected empty data, got %d bytes", len(record.Data))
    }
}

func TestAppendLarge(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()

    largeData := make([]byte, 10*1024*1024)
    for i := range largeData {
        largeData[i] = byte(i % 256)
    }

    offset, err := wal.Append(ctx, largeData)
    if err != nil {
        t.Fatalf("failed to append large data: %v", err)
    }

    record, err := wal.Read(ctx, offset)
    if err != nil {
        t.Fatalf("failed to read large record: %v", err)
    }

    if len(record.Data) != len(largeData) {
        t.Errorf("data length mismatch: expected %d, got %d",
            len(largeData), len(record.Data))
    }

    for i := range largeData {
        if record.Data[i] != largeData[i] {
            t.Errorf("data mismatch at index %d: expected %d, got %d",
                i, largeData[i], record.Data[i])
            break
        }
    }
}

func TestSameOffset(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()
    # https:#x.com/iavins/status/1860299083056849098
    data := []byte("threads are evil")
    _, err := wal.Append(ctx, data)
    if err != nil {
        t.Fatalf("failed to append first record: %v", err)
    }

    # reset the WAL counter so that it uses the same offset
    wal.length = 0
    _, err = wal.Append(ctx, data)
    if err == nil {
        t.Error("expected error when appending at same offset, got nil")
    }
}

func TestLastRecord(t *testing.T) {
    wal, cleanup := getWAL(t)
    defer cleanup()
    ctx := context.Background()

    record, err := wal.LastRecord(ctx)
    if err == nil {
        t.Error("expected error when getting last record from empty WAL, got nil")
    }

    var lastData []byte
    for i := 0; i < 1234; i++ {
        lastData = []byte(generateRandomStr())
        _, err = wal.Append(ctx, lastData)
        if err != nil {
            t.Fatalf("failed to append record: %v", err)
        }
    }

    record, err = wal.LastRecord(ctx)
    if err != nil {
        t.Fatalf("failed to get last record: %v", err)
    }

    if record.Offset != 1234 {
        t.Errorf("expected offset 1234, got %d", record.Offset)
    }

    if string(record.Data) != string(lastData) {
        t.Errorf("data mismatch: expected %q, got %q", lastData, record.Data)
    }
}
"""