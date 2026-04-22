CC ?= cc
CFLAGS ?= -Wall -Wextra -std=c11 -Iinclude
SRC := src/parser.c src/encoder.c src/decoder.c src/crc32.c
OBJ := $(SRC:.c=.o)

all: lib

lib: $(OBJ)
	$(AR) rcs librtimg.a $(OBJ)

clean:
	rm -f $(OBJ) librtimg.a
