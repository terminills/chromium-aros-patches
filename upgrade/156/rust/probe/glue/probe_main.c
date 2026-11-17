extern int rust_probe_main(void);
int aros_argc;
char **aros_argv;
int main(int argc, char **argv) { aros_argc=argc; aros_argv=argv; return rust_probe_main(); }
