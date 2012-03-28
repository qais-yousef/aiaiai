/*
 * Copyright 2012 Intel Corporation
 * Author: Artem Bityutskiy <dedekind1@gmail.com>
 * License: GPLv2
 *
 * Credits to Eric Melski for the idea and reference implementation:
 * http://www.cmcrossroads.com/ask-mr-make/12909-descrambling-parallel-build-logs
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <getopt.h>
#include <stdbool.h>
#include <sys/wait.h>
#include <sys/file.h>

#define PROGRAM_NAME "serialize-log"
#define TMPFILE_NAME "/tmp/" PROGRAM_NAME ".XXXXXX"
#define BUF_SIZE 8192

static char *lockfile;
static char *commands;
static bool split = false;

static void usage(FILE *dest, int status)
{
	fprintf(dest,
"Usage: " PROGRAM_NAME " -l <lockfile> [options]\n"
"\n"
"Capture entire stdout and stderr output of shell <commands> and print it\n"
"when the commands finish. The idea is that commands should also use\n"
PROGRAM_NAME " to serizlize (descrabmle) the output. This can be used\n"
"with parallell make (e.g., -j10) to descramble the build log and make it\n"
"readable. For example:\n"
"\n"
PROGRAM_NAME " -l lock -c \"make SHELL='" PROGRAM_NAME " -l lock' -j20\"\n"
"\n"
"The lockfile is a mandatory parameter which is used to make sure than only\n"
"one process prints to stdout/stderr at a time.\n"
"\n"
"Options:\n"
"  -l, --lockfile=FILE   path to the file to use for serializing the output;\n"
"  -c  COMMANDS          the commands to execute in a shell;\n"
"  -s, --split           split stderr and stdout;\n"
"  -h, --help            print help message and exit.\n"
);
	exit(status);
}

static const struct option long_options[] = {
	{ .name = "lock-file", .has_arg = 1, .flag = NULL, .val = 'l' },
	{ .name = "split",     .has_arg = 1, .flag = NULL, .val = 's' },
	{ .name = "",          .has_arg = 1, .flag = NULL, .val = 'c' },
	{ .name = "help",      .has_arg = 0, .flag = NULL, .val = 'h' },
	{ NULL, 0, NULL, 0},
};

static void parse_options(int argc, char *argv[])
{
	if (argc < 2) {
		fprintf(stderr, "Error: please, specify the lock file\n");
		usage(stderr, EXIT_FAILURE);
	}

	while (1) {
		int key;

		key = getopt_long(argc, argv, "l:c:sh", long_options, NULL);
		if (key == -1)
			break;

		switch (key) {
		case 'l':
			lockfile = optarg;
			break;
		case 'c':
			commands = optarg;
			break;
		case 's':
			split = true;
			break;
		case 'h':
			usage(stdout, EXIT_SUCCESS);
		case ':':
			fprintf(stderr, "Error: parameter is missing\n");
		default:
			fprintf(stderr, "Use -h for help\n");
			exit(EXIT_FAILURE);
		}
	}

	if (!lockfile) {
		fprintf(stderr, "Error: please, specify the lockfile\n");
		exit(EXIT_FAILURE);
	}

	if (!commands)
		exit(EXIT_SUCCESS);
}

int main(int argc, char *argv[])
{
	int fstdout, fstderr = -1, lockfd;
	char fstdout_name[sizeof(TMPFILE_NAME)];
	char fstderr_name[sizeof(TMPFILE_NAME)];
	char buf[BUF_SIZE];
	pid_t child;
	int status = 0;
	ssize_t rd;

	parse_options(argc, argv);

	/* Create temporary files for stdout and stderr of the child program */
	memcpy(fstdout_name, TMPFILE_NAME, sizeof(TMPFILE_NAME));
	memcpy(fstderr_name, TMPFILE_NAME, sizeof(TMPFILE_NAME));
	fstdout = mkstemp(fstdout_name);
	if (fstdout == -1) {
		perror("mkstemp");
		exit(EXIT_FAILURE);
	}
	if (split) {
		fstderr = mkstemp(fstderr_name);
		if (fstderr == -1) {
			perror("mkstemp");
			goto out_fstdout;
		}
	}

	child = fork();
	if (child == -1) {
		perror("fork");
		goto out_fstderr;
	}

	if (child == 0) {
		char * const sh_argv[4] = { "/bin/sh", "-c", commands, 0 };

		close(1);
		close(2);

		if (dup2(fstdout, 1) == -1)
			exit(EXIT_FAILURE);
		if (dup2(split ? fstderr : fstdout, 2) == -1)
			exit(EXIT_FAILURE);
		if (execvp("/bin/sh", sh_argv) == -1) {
			perror("execvp");
			exit(EXIT_FAILURE);
		}

		exit(EXIT_FAILURE);
	}

	if (waitpid(child, &status, 0) == -1) {
		perror("waitpid");
		goto out_fstderr;
	}

	if (lseek(fstdout, 0, SEEK_SET) == -1) {
		perror("lseek");
		goto out_fstderr;
	}
	if (split) {
		if (lseek(fstderr, 0, SEEK_SET) == -1) {
			perror("lseek");
			goto out_fstderr;
		}
	}

	lockfd = open(lockfile, O_WRONLY | O_CREAT, S_IRUSR | S_IWUSR);
	if (lockfd == -1) {
		perror("open");
		goto out_fstderr;
	}

	if (flock(lockfd, LOCK_EX) == -1) {
		perror("flock");
		goto out_fstderr;
	}

	while ((rd = read(fstdout, buf, BUF_SIZE)) > 0) {
		if (write(1, buf, rd) != rd) {
			perror("write");
			goto out_unlock;
		}
	}
	if (rd == -1) {
		perror("read");
		goto out_unlock;
	}

	if (split) {
		while ((rd = read(fstderr, buf, BUF_SIZE)) > 0) {
			if (write(2, buf, rd) != rd) {
				perror("write");
				goto out_unlock;
			}
		}
		if (rd == -1) {
			perror("read");
			goto out_unlock;
		}
	}

	flock(lockfd, LOCK_UN);
	close(lockfd);
	if (split) {
		close(fstderr);
		unlink(fstderr_name);
	}
	close(fstdout);
	unlink(fstdout_name);
	exit(WEXITSTATUS(status));

out_unlock:
	flock(lockfd, LOCK_UN);
	close(lockfd);
out_fstderr:
	if (split) {
		close(fstderr);
		unlink(fstderr_name);
	}
out_fstdout:
	close(fstdout);
	unlink(fstdout_name);
	return EXIT_FAILURE;
}
