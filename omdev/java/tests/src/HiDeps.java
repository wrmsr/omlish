//usr/bin/true; exec om java run "$0" "$@"
/* @omlish-jdeps [
    "com.google.guava:guava:33.5.0"
] */
public class Hi {
    public static void main(String[] args) {
        System.out.println(args);
        for (String arg : args) {
            System.out.println(arg);
        }
    }
}
