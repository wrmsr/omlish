//usr/bin/true; exec om java run "$0" "$@"
public class Hi {
    public static void main(String[] args) {
        System.out.printf("Arguments (%d):\n", args.length);
        for (int i = 0; i < args.length; ++i) {
            System.out.printf("argv[%d]: %s\n", i, args[i]);
        }
    }
}
