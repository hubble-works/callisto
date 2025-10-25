"""Utility for augmenting diffs with line numbers."""


def augment_diff_with_line_numbers(diff: str) -> str:
    """
    Augment a unified diff with line numbers at the beginning of each line.

    This helps AI models provide accurate line number references when reviewing code.
    The function adds the actual line number from the "new" file (right side) for
    added and unchanged lines, making it easier to reference specific lines in reviews.

    Args:
        diff: A unified diff string (output from git diff)

    Returns:
        The same diff with line numbers prepended to each content line

    Example:
        Input:
            @@ -10,5 +10,6 @@ def example():
             def hello():
            -    print("old")
            +    print("new")
            +    return True

        Output:
            @@ -10,5 +10,6 @@ def example():
            10:     def hello():
            -:    -    print("old")
            11:    +    print("new")
            12:    +    return True
            13:
    """
    lines = diff.split("\n")
    augmented_lines = []
    current_right_line = 0

    for line in lines:
        # Parse hunk headers to get starting line numbers
        if line.startswith("@@"):
            # Extract the right side line number (new file)
            # Format: @@ -left_start,left_count +right_start,right_count @@
            parts = line.split()
            for part in parts:
                if part.startswith("+"):
                    # Extract starting line number
                    right_info = part[1:].split(",")[0]
                    current_right_line = int(right_info)
                    break
            augmented_lines.append(line)
        elif line.startswith("---") or line.startswith("+++"):
            # File headers - keep as is
            augmented_lines.append(line)
        elif line.startswith("diff --git") or line.startswith("index "):
            # Diff metadata - keep as is
            augmented_lines.append(line)
        elif line.startswith("-"):
            # Deleted line - no line number in new file
            augmented_lines.append(f"-: {line}")
        elif line.startswith("+"):
            # Added line - has line number in new file
            augmented_lines.append(f"{current_right_line}: {line}")
            current_right_line += 1
        elif line.startswith(" "):
            # Context line - has line number in new file
            augmented_lines.append(f"{current_right_line}: {line}")
            current_right_line += 1
        else:
            # Other lines (empty, metadata) - keep as is
            if current_right_line > 0:
                # If we're in a hunk, treat empty lines as context
                augmented_lines.append(f"{current_right_line}: {line}")
                current_right_line += 1
            else:
                augmented_lines.append(line)

    return "\n".join(augmented_lines)
