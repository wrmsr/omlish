import org.junit.Test;

import java.util.Objects;

import static org.junit.Assert.assertEquals;

public class SubsTest
{
    //region A

    public interface ANode<A>
    {
        <R, C> R acceptAVisitor(AVisitor<A, R, C> visitor, C ctx);
    }

    public interface AVisitor<A, R, C>
    {
        default R visitANode(ANode<A> node, C ctx)
        {
            throw new IllegalStateException(Objects.toString(node));
        }

        default R visitAAdd(AAdd<A> node, C ctx)
        {
            return visitANode(node, ctx);
        }

        default R visitAConst(AConst<A> node, C ctx)
        {
            return visitANode(node, ctx);
        }
    }

    public static class AAdd<A>
            implements ANode<A>
    {
        public final ANode<A> left;
        public final ANode<A> right;

        public AAdd(ANode<A> left, ANode<A> right)
        {
            this.left = left;
            this.right = right;
        }

        @Override
        public <R, C> R acceptAVisitor(AVisitor<A, R, C> visitor, C ctx)
        {
            return visitor.visitAAdd(this, ctx);
        }
    }

    public static class AConst<A>
            implements ANode<A>
    {
        public final int val;

        public AConst(int val)
        {
            this.val = val;
        }

        @Override
        public <R, C> R acceptAVisitor(AVisitor<A, R, C> visitor, C ctx)
        {
            return visitor.visitAConst(this, ctx);
        }
    }

    public static <A> AAdd<A> aAdd(ANode<A> left, ANode<A> right)
    {
        return new AAdd<>(left, right);
    }

    public static <A> AConst<A> aConst(int val)
    {
        return new AConst<>(val);
    }

    //endregion

    //region B

    public interface BNode
            extends ANode<BNode>
    {
        default <R, C> R acceptAVisitor(AVisitor<BNode, R, C> visitor, C ctx)
        {
            return acceptBVisitor((BVisitor<R, C>) visitor, ctx);
        }

        <R, C> R acceptBVisitor(BVisitor<R, C> visitor, C ctx);
    }

    public interface BVisitor<R, C>
            extends AVisitor<BNode, R, C>
    {
        default R visitBNode(BNode node, C ctx)
        {
            return visitANode(node, ctx);
        }

        default R visitBAdd(BAdd node, C ctx)
        {
            return visitAAdd(node, ctx);
        }

        default R visitBConst(BConst node, C ctx)
        {
            return visitAConst(node, ctx);
        }

        default R visitBMul(BMul node, C ctx)
        {
            return visitBNode(node, ctx);
        }
    }

    public static class BAdd
            extends AAdd<BNode>
            implements BNode
    {
        public BAdd(ANode<BNode> left, ANode<BNode> right)
        {
            super(left, right);
        }

        @Override
        public <R, C> R acceptBVisitor(BVisitor<R, C> visitor, C ctx)
        {
            return visitor.visitBAdd(this, ctx);
        }
    }

    public static class BConst
            extends AConst<BNode>
            implements BNode
    {
        public BConst(int val)
        {
            super(val);
        }

        @Override
        public <R, C> R acceptBVisitor(BVisitor<R, C> visitor, C ctx)
        {
            return visitor.visitBConst(this, ctx);
        }
    }

    public static class BMul
            implements BNode
    {
        public final BNode left;
        public final BNode right;

        public BMul(BNode left, BNode right)
        {
            this.left = left;
            this.right = right;
        }

        @Override
        public <R, C> R acceptBVisitor(BVisitor<R, C> visitor, C ctx)
        {
            return visitor.visitBMul(this, ctx);
        }
    }

    public static BAdd bAdd(BNode left, BNode right)
    {
        return new BAdd(left, right);
    }

    public static BConst bConst(int val)
    {
        return new BConst(val);
    }

    public static BMul bMul(BNode left, BNode right)
    {
        return new BMul(left, right);
    }

    //endregion

    //region AEval

    public static class AEval<A>
            implements AVisitor<A, Integer, Void>
    {
        @Override
        public Integer visitAAdd(AAdd<A> node, Void ctx)
        {
            return node.left.acceptAVisitor(this, ctx) + node.right.acceptAVisitor(this, ctx);
        }

        @Override
        public Integer visitAConst(AConst<A> node, Void ctx)
        {
            return node.val;
        }
    }

    public static <A> int aEval(ANode<A> node)
    {
        return node.acceptAVisitor(new AEval<A>(), null);
    }

    //endregion

    //region BEval

    public static class BEval
            extends AEval<BNode>
            implements BVisitor<Integer, Void>
    {
        @Override
        public Integer visitBMul(BMul node, Void ctx)
        {
            return node.left.acceptBVisitor(this, ctx) * node.right.acceptBVisitor(this, ctx);
        }
    }

    public static int bEval(BNode node)
    {
        return node.acceptBVisitor(new BEval(), null);
    }

    //endregion

    @Test
    public void testSubs()
            throws Throwable
    {
        assertEquals(aEval(aConst(1)), 1);
        assertEquals(aEval(aAdd(aConst(1), aConst(2))), 1 + 2);
        assertEquals(bEval(bMul(bConst(2), bConst(3))), 2 * 3);
        assertEquals(bEval(bMul(bConst(2), bAdd(bConst(3), bConst(4)))), 2 + (3 * 4));
        assertEquals(bEval(bMul(bConst(2), bAdd(bConst(3), bMul(bConst(4), bConst(5))))), 2 * (3 + (4 * 5)));
    }
}
