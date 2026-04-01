/**
 * SSE (Server-Sent Events) Decoder Module
 *
 * Provides utilities for decoding SSE streams using TransformStream.
 */

/**
 * Creates a TransformStream that decodes SSE formatted data.
 *
 * SSE format:
 * data: {json}\n\n
 * data: [DONE]\n\n
 *
 * @returns {TransformStream} A transform stream that converts SSE bytes to parsed objects
 */
window.createSSEDecoder = function() {
    let buffer = '';

    return new TransformStream({
        transform(chunk, controller) {
            // Decode the chunk and add to buffer
            buffer += new TextDecoder().decode(chunk);

            // Split by double newlines (SSE message separator)
            const lines = buffer.split('\n');

            // Process all complete lines (keep last incomplete line in buffer)
            buffer = lines.pop() || '';

            for (const line of lines) {
                const trimmedLine = line.trim();

                if (trimmedLine === '') {
                    continue;
                }

                // SSE lines start with "data: "
                if (trimmedLine.startsWith('data: ')) {
                    const data = trimmedLine.slice(6);

                    // Check for [DONE] signal
                    if (data === '[DONE]') {
                        controller.enqueue({ done: true });
                        continue;
                    }

                    // Parse JSON data
                    try {
                        const parsed = JSON.parse(data);
                        controller.enqueue(parsed);
                    } catch (e) {
                        console.error('Failed to parse SSE data:', data, e);
                    }
                }
            }
        },

        flush(controller) {
            // Process any remaining data in buffer
            if (buffer.trim()) {
                const trimmedLine = buffer.trim();
                if (trimmedLine.startsWith('data: ')) {
                    const data = trimmedLine.slice(6);
                    if (data === '[DONE]') {
                        controller.enqueue({ done: true });
                    } else {
                        try {
                            const parsed = JSON.parse(data);
                            controller.enqueue(parsed);
                        } catch (e) {
                            console.error('Failed to parse SSE data:', data, e);
                        }
                    }
                }
            }
        }
    });
}

/**
 * Fetches an SSE stream and processes it with a callback.
 *
 * @param {string} url - The URL to fetch
 * @param {Object} options - Fetch options (method, headers, body, etc.)
 * @param {Function} onChunk - Callback for each parsed SSE chunk
 * @returns {Promise<void>}
 */
window.fetchSSEStream = async function(url, options, onChunk) {
    const response = await fetch(url, options);

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
        throw new Error('Response body is null');
    }

    const reader = response.body
        .pipeThrough(window.createSSEDecoder())
        .getReader();

    try {
        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            // Check if this is the [DONE] signal
            if (value.done) {
                break;
            }

            // Call the chunk handler
            await onChunk(value);
        }
    } finally {
        reader.releaseLock();
    }
}
