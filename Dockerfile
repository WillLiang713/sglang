FROM lmsysorg/sglang:latest

ARG SGLANG_INSTALL_SOURCE=pypi

# Install the latest sglang on top of the pinned runtime base image.
RUN if [ "$SGLANG_INSTALL_SOURCE" = "source" ]; then \
      uv pip install --system --upgrade "git+https://github.com/sgl-project/sglang.git#subdirectory=python"; \
    else \
      uv pip install --system --upgrade sglang; \
    fi
