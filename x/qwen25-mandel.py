"""
https://simonwillison.net/2024/Nov/12/qwen25-coder/

--

uv run --with mlx-lm \
  mlx_lm.generate \
  --model mlx-community/Qwen2.5-Coder-32B-Instruct-8bit \
  --max-tokens 4000 \
  --prompt 'write me a python function that renders a mandelbrot fractal as wide as the current terminal'

--

Prompt: <|im_start|>system
You are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>
<|im_start|>user
write me a python function that renders a mandelbrot fractal as wide as the current terminal<|im_end|>
<|im_start|>assistant

Certainly! To render a Mandelbrot fractal in the terminal, we need to map the complex plane to the terminal's wi
dth and height. The Mandelbrot set is defined by the recurrence relation \( z_{n+1} = z_n^2 + c \), where \( z \
) and \( c \) are complex numbers, and \( z_0 = 0 \). A point \( c \) is part of the Mandelbrot set if the seque
nce does not diverge to infinity.

Here's a Python function that renders a Mandelbrot fractal as wide as the current terminal:

```python
...
```

### Explanation:
1. **Terminal Size**: The `shutil.get_terminal_size()` function is used to get the width and height of the terminal.
2. **Complex Plane Mapping**: The region of the complex plane to render is defined by `x_min`, `x_max`, `y_min`, and `y_max`. The step sizes `x_step` and `y_step` are calculated to map the pixel positions to the complex plane.
3. **Mandelbrot Function**: The `mandelbrot` function calculates the number of iterations for a given complex number `c` before it diverges.
4. **Character Mapping**: A list of characters is used to represent different levels of iteration. The number of iterations is mapped to a character in this list.
5. **Rendering**: The function iterates over each pixel in the terminal, maps it to a point in the complex plane, calculates the number of iterations, and prints the corresponding character.

You can run this script in a terminal to see the Mandelbrot fractal rendered in ASCII characters. Adjust the `max_iter` variable to increase or decrease the detail of the fractal.
==========
Prompt: 49 tokens, 76.084 tokens-per-sec
Generation: 723 tokens, 13.640 tokens-per-sec
Peak memory: 32.685 GB
"""
import shutil


def mandelbrot(c, max_iter):
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z * z + c
        n += 1
    return n


def render_mandelbrot():
    # Get the terminal width and height
    terminal_width, terminal_height = shutil.get_terminal_size()

    # Define the region of the complex plane to render
    x_min, x_max = -2.0, 1.0
    y_min, y_max = -1.5, 1.5

    # Calculate the step sizes
    x_step = (x_max - x_min) / terminal_width
    y_step = (y_max - y_min) / terminal_height

    # Define the maximum number of iterations
    max_iter = 100

    # Create a list of characters to represent different levels of iteration
    chars = " .:-=+*#%@"

    # Render the Mandelbrot set
    for y in range(terminal_height):
        for x in range(terminal_width):
            # Map pixel position to a point in the complex plane
            real = x_min + x * x_step
            imag = y_min + y * y_step
            c = complex(real, imag)
            # Determine the number of iterations
            m = mandelbrot(c, max_iter)
            # Map the number of iterations to a character
            char = chars[min(m, len(chars) - 1)]
            print(char, end='')
        print()


if __name__ == "__main__":
    render_mandelbrot()
