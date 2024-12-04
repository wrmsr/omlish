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
import abc
import dataclasses as dc
import hashlib
import io
import struct
import typing as ta


##


@dc.dataclass(frozen=True)
class S3PutObjectInput:
    bucket: str
    key: str
    body: bytes

    _: dc.KW_ONLY

    if_none_match: str | None = None


@dc.dataclass(frozen=True)
class S3GetObjectInput:
    bucket: str
    key: str


@dc.dataclass(frozen=True)
class S3GetObjectResult:
    body: bytes


@dc.dataclass(frozen=True)
class S3ListObjectsV2Input:
    bucket: str
    prefix: str


class S3Client(abc.ABC):
    @abc.abstractmethod
    def put_object(self, input: S3PutObjectInput) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def get_object(self, input: S3GetObjectInput) -> S3GetObjectResult:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class S3ListObjectsV2PaginatorItem:
    key: str


@dc.dataclass(frozen=True)
class S3ListObjectsV2PaginatorPage:
    @property
    @abc.abstractmethod
    def contents(self) -> ta.Sequence[S3ListObjectsV2PaginatorItem]:
        raise NotImplementedError


class S3ListObjectsV2Paginator(abc.ABC):
    @abc.abstractmethod
    def has_more_pages(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def next_page(self) -> S3ListObjectsV2PaginatorPage:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class WalRecord:
    offset: int
    data: bytes


class Wal(abc.ABC):
    @abc.abstractmethod
    def append(self, data: bytes) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, offset: int) -> WalRecord:
        raise NotImplementedError

    @abc.abstractmethod
    def last_record(self) -> WalRecord:
        raise NotImplementedError


##


class S3Wal(Wal):
    def __init__(
        self,
        client: S3Client,
        bucket_name: str,
        prefix: str,
    ) -> None:
        super().__init__()
        
        self._client = client
        self._bucket_name = bucket_name
        self._prefix = prefix
        
        self._length = 0

    def _get_object_key(self, offset: int) -> str:
        return self._prefix + '/' + ('%020d' % (offset,))

    def _get_offset_from_key(self, key: str) -> int:
        # skip the `w.prefix` and '/'
        num_str = key[len(self._prefix)+1:]
        return int(num_str, 10, 64)

    def _calculate_checksum(self, buf: bytes) -> bytes:
        hash_obj = hashlib.sha256()
        hash_obj.update(buf)
        return hash_obj.digest()

    def _validate_checksum(self, data: bytes) -> bool:
        stored_checksum = data[-32:]
        record_data = data[:-32]
        return stored_checksum == self._calculate_checksum(record_data)


    def _prepare_body(self, offset: int, data: bytes) -> bytes:
        buf = io.BytesIO()
        buf.write(struct.pack('>Q', offset))
        buf.write(data)
        checksum = self._calculate_checksum(buf.getvalue())
        buf.write(checksum)
        return buf.getvalue()

    def append(self, data: bytes) -> int:
        next_offset = self._length + 1

        buf = self._prepare_body(next_offset, data)

        self._client.put_object(S3PutObjectInput(
            bucket=self._bucket_name,
            key=self._get_object_key(next_offset),
            body=buf,
            if_none_match='*',
        ))

        self._length = next_offset
        return next_offset

    def read(self, offset: int) -> WalRecord:
        key = self._get_object_key(offset)

        result = self._client.get_object(S3GetObjectInput(
            bucket=self._bucket_name,
            key=key,
        ))
        data = result.body

        if len(data) < 40:
            raise Exception('invalid record: data too short')

        stored_offset = struct.unpack('>Q', data[:8])[0]
        if stored_offset != offset:
            raise Exception(f'offset mismatch: expected {offset}, got {stored_offset}')
        if not self._validate_checksum(data):
            raise Exception('checksum mismatch')

        return WalRecord(
            offset=stored_offset,
            data=data[8:-32],
        )

    def last_record(self) -> WalRecord:
        paginator = S3ListObjectsV2Paginator(
            self._client,
            S3ListObjectsV2Input(
                bucket=self._bucket_name,
                prefix=self._prefix + '/',
            ),
        )

        max_offset: int = 0
        while paginator.has_more_pages():
            output = paginator.next_page()
            for obj in output.contents:
                key = obj.key
                offset = self._get_offset_from_key(key)
                if offset > max_offset:
                    max_offset = offset

        if max_offset == 0:
            raise Exception('wal is empty')

        self._length = max_offset
        return self.read(max_offset)


##


"""
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