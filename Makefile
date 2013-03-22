CFLAGS = -O2 -g -Wextra

all:
	$(CC) $(CFLAGS) -o aiaiai-locker aiaiai-locker.c
	make -C external

clean:
	$(RM) aiaiai-locker
	make -C external clean
