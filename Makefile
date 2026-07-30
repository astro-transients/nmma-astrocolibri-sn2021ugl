# ==============================================================================
# nmma-astrocolibri-sn2021ugl - Reproducibility Makefile
# ==============================================================================
#
# Usage:
#   make setup                                          : compile MultiNest/PyMultiNest, install Python env (uv)
#   make fit MODEL=v19-1993j-corr CONFIG=full_baseline_with_upper_limits : replay one archived fit
#   make plot MODELS="v19-1993j-corr nugent-hyper" CONFIG=full_baseline_with_upper_limits : overlay best-fit light curves
#
# Prerequisites (Mac):
#   brew install cmake gfortran openblas
# Prerequisites (Linux):
#   apt install cmake gfortran libopenblas-dev liblapack-dev
# ==============================================================================

UNAME := $(shell uname -s)

ifeq ($(UNAME), Darwin)
    BLAS_LIB := /opt/homebrew/opt/openblas/lib/libopenblas.dylib
    LAPACK_LIB := /opt/homebrew/opt/openblas/lib/libopenblas.dylib
    LIB_EXT := dylib
    LIB_PATH_VAR := DYLD_LIBRARY_PATH
else
    ARCH := $(shell dpkg-architecture -qDEB_HOST_MULTIARCH 2>/dev/null || echo x86_64-linux-gnu)
    BLAS_LIB := /usr/lib/$(ARCH)/libopenblas.so
    LAPACK_LIB := /usr/lib/$(ARCH)/liblapack.so
    LIB_EXT := so
    LIB_PATH_VAR := LD_LIBRARY_PATH
endif

setup-multinest:
	rm -rf /tmp/multinest
	git clone https://github.com/JohannesBuchner/MultiNest /tmp/multinest
	cd /tmp/multinest/build && cmake .. \
		-DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
		-DCMAKE_BUILD_TYPE=Release \
		-DCMAKE_DISABLE_FIND_PACKAGE_MPI=ON \
		-DMPI_C_COMPILER="" \
		-DMPI_CXX_COMPILER="" \
		-DMPI_Fortran_COMPILER="" \
		-DBLAS_LIBRARIES=$(BLAS_LIB) \
		-DLAPACK_LIBRARIES=$(LAPACK_LIB)
	cd /tmp/multinest/build && make -j1
	mkdir -p $(HOME)/.local/lib
	cp /tmp/multinest/lib/libmultinest.$(LIB_EXT) $(HOME)/.local/lib/
	cp /tmp/multinest/lib/libmultinest.a $(HOME)/.local/lib/

setup: setup-multinest
	rm -rf /tmp/pymultinest
	git clone https://github.com/JohannesBuchner/PyMultiNest /tmp/pymultinest
	uv sync
	uv pip install /tmp/pymultinest
	echo 'export $(LIB_PATH_VAR)=$(HOME)/.local/lib:$$$(LIB_PATH_VAR)' >> .venv/bin/activate

# `uv run` does NOT source .venv/bin/activate (it just invokes the venv's
# interpreter directly), so the $(LIB_PATH_VAR) export appended there by
# `make setup` is never picked up this way, set it explicitly here too,
# or PyMultiNest fails at runtime with a cryptic
# "AttributeError: dlsym(RTLD_DEFAULT, run): symbol not found"
# (it never actually loaded libmultinest).
fit:
	@if [ -z "$(MODEL)" ] || [ -z "$(CONFIG)" ]; then \
		echo "Usage: make fit MODEL=<model_key> CONFIG=<config_name>"; \
		echo "  e.g. make fit MODEL=v19-1993j-corr CONFIG=full_baseline_with_upper_limits"; \
		exit 1; \
	fi
	$(LIB_PATH_VAR)=$(HOME)/.local/lib:$$$(LIB_PATH_VAR) uv run python scripts/run_fit.py $(CONFIG) $(MODEL)

plot:
	@if [ -z "$(MODELS)" ] || [ -z "$(CONFIG)" ]; then \
		echo "Usage: make plot MODELS=\"model1 model2\" CONFIG=<config_name>"; \
		exit 1; \
	fi
	@mkdir -p results/$(CONFIG)
	$(LIB_PATH_VAR)=$(HOME)/.local/lib:$$$(LIB_PATH_VAR) uv run python scripts/plot_compare_models_public.py \
		--outdir data/SN2021ugl_NMMA_posteriors/$(CONFIG) \
		--candname SN_2021ugl \
		--models $(MODELS) \
		--output results/$(CONFIG)/SN_2021ugl_compare_$(subst $() ,_,$(MODELS)).png
