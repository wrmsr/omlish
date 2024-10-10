SHELL:=/bin/bash

ANTLR_VERSION=4.13.1

.PHONY: antlr
antlr:
	if [ ! -f "antlr-$(ANTLR_VERSION)-complete.jar" ] ; then \
		curl \
			--proto '=https' \
			--tlsv1.2 \
			"https://www.antlr.org/download/antlr-$(ANTLR_VERSION)-complete.jar" \
			-o "antlr-$(ANTLR_VERSION)-complete.jar" ; \
	fi


RUNTIME_DIR=antlr4/runtime/Cpp/runtime

#RUNTIME_SOURCES=$(wildcard ${RUNTIME_DIR}/*.cpp) $(wildcard ${RUNTIME_DIR}*/*.cpp)
#
#.PHONY: runtime
#runtime:
#	echo $(RUNTIME_SOURCES)


RUNTIME_SRC_DIR := ${RUNTIME_DIR}/src
RUNTIME_OBJ_DIR := ${RUNTIME_DIR}/obj
RUNTIME_SRC_FILES := $(wildcard $(RUNTIME_SRC_DIR)/*.cpp)
RUNTIME_OBJ_FILES := $(patsubst $(RUNTIME_SRC_DIR)/%.cpp,$(RUNTIME_OBJ_DIR)/%.o,$(RUNTIME_SRC_FILES))

CXXFLAGS=-std=c++17 -I ${RUNTIME_DIR}/src

main.exe: $(RUNTIME_OBJ_FILES)
	g++ $(LDFLAGS) -o $@ $^

$(RUNTIME_OBJ_DIR)/%.o: $(RUNTIME_SRC_DIR)/%.cpp
	g++ $(CXXFLAGS) -c -o $@ $<
	

PYBIND_VERSION=2.11.1
