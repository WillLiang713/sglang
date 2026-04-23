FROM lmsysorg/sglang:latest

# Install the latest sglang directly from source.
RUN uv pip install --system --upgrade "git+https://github.com/sgl-project/sglang.git#subdirectory=python"
