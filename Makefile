# Compiler
CC = gcc

# Compiler flags
CFLAGS = -Wall -g

# Source files
SRCS = jpeg_parser_phase1_marker_parsing.c \
       jpeg_parser_phase2_huffman_decoding.c \
       jpeg_parser_phase3_dct_reconstruction.c \
       jpeg_parser_phase4_dct_encoding_and_writing.c

# Object files - corresponding to source files
OBJS = $(SRCS:.c=.o)

# Target executable name
TARGET = jpeg_parser

# Default rule: build the target executable
all: $(TARGET)

# Rule to link object files into the target executable
$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $(TARGET) $(OBJS)

# Rule to compile .c source files into .o object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean rule: remove object files and the target executable
clean:
	rm -f $(OBJS) $(TARGET)

# Phony targets
.PHONY: all clean
