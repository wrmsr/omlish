//usr/bin/true; exec om java run "$0" "$@"
/* @omlish-jdeps [
    "com.google.guava:guava:33.5.0-jre"
] */
import com.google.common.base.Preconditions;
import com.google.common.collect.ImmutableList;

public class HiDeps {
    public static void main(String[] args) {
        // Use Guava in a real way, but keep behavior identical
        Preconditions.checkNotNull(args, "args");

        ImmutableList<String> argv = ImmutableList.copyOf(args);

        System.out.printf("Arguments (%d):\n", argv.size());
        for (int i = 0; i < argv.size(); ++i) {
            System.out.printf("argv[%d]: %s\n", i, argv.get(i));
        }
    }
}
