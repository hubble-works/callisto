"""Tests for diff augmentation utility."""

from app.utils.diff_augmenter import augment_diff_with_line_numbers


class TestAugmentDiffWithLineNumbers:
    """Test cases for augment_diff_with_line_numbers function."""

    def test_simple_addition(self):
        """Test diff with only added lines."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,3 +10,5 @@ def example():
     return True
+    # New comment
+    print("added")"""

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,3 +10,5 @@ def example():
10:      return True
11: +    # New comment
12: +    print("added")"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_simple_deletion(self):
        """Test diff with only deleted lines."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,4 +10,2 @@ def example():
     return True
-    # Old comment
-    print("removed")"""

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,4 +10,2 @@ def example():
10:      return True
-: -    # Old comment
-: -    print("removed")"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_mixed_changes(self):
        """Test diff with added, deleted, and context lines."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,5 +10,6 @@ def example():
     def hello():
-    print("old")
+    print("new")
+    return True
     """

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,5 +10,6 @@ def example():
10:      def hello():
-: -    print("old")
11: +    print("new")
12: +    return True
13:      """

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_multiple_hunks(self):
        """Test diff with multiple hunks."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -5,3 +5,4 @@ class Example:
     def __init__(self):
+        self.name = "test"
         pass
@@ -20,2 +21,3 @@ class Example:
     def method(self):
+        # New comment
         return True"""

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -5,3 +5,4 @@ class Example:
5:      def __init__(self):
6: +        self.name = "test"
7:          pass
@@ -20,2 +21,3 @@ class Example:
21:      def method(self):
22: +        # New comment
23:          return True"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_empty_diff(self):
        """Test empty diff string."""
        diff = ""
        expected = ""
        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_context_only_diff(self):
        """Test diff with only context lines."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,3 +10,3 @@ def example():
     line1
     line2
     line3"""

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -10,3 +10,3 @@ def example():
10:      line1
11:      line2
12:      line3"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_new_file(self):
        """Test diff for a newly created file."""
        diff = """diff --git a/new_file.py b/new_file.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
+def new_function():
+    pass
+    return True"""

        expected = """diff --git a/new_file.py b/new_file.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1,3 @@
1: +def new_function():
2: +    pass
3: +    return True"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected

    def test_line_number_continuation(self):
        """Test that line numbers continue correctly through the diff."""
        diff = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -100,7 +100,8 @@ def large_function():
     line100
     line101
-    old_line102
+    new_line102
+    added_line103
     line104
     line105
     line106"""

        expected = """diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -100,7 +100,8 @@ def large_function():
100:      line100
101:      line101
-: -    old_line102
102: +    new_line102
103: +    added_line103
104:      line104
105:      line105
106:      line106"""

        result = augment_diff_with_line_numbers(diff)
        assert result == expected
