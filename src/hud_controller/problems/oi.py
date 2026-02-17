"""
OI-style algorithmic problem definitions.

Each problem should have corresponding test data in:
/problems/{problem_id}/input/{1..n}.txt
/problems/{problem_id}/output/{1..n}.txt
"""

import logging

from hud_controller.spec import OI_PROBLEM_REGISTRY, OIProblemSpec

logger = logging.getLogger(__name__)


# Example problem: Two Sum
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="two_sum",
        description="""Given an array of integers and a target sum, find two numbers that add up to the target.

Input format:
- First line: Two integers N (1 <= N <= 10^5) and T (-10^9 <= T <= 10^9)
  - N is the size of the array
  - T is the target sum
- Second line: N space-separated integers A[i] (-10^9 <= A[i] <= 10^9)

Output format:
- Two space-separated 0-based indices i and j (i < j) such that A[i] + A[j] = T
- If multiple solutions exist, output any one of them
- It is guaranteed that a solution exists

Example:
Input:
5 9
2 7 11 15 1

Output:
0 1

Explanation: A[0] + A[1] = 2 + 7 = 9
""",
        difficulty="easy",
        time_limit_seconds=1,
    )
)

# KOMPIĆI (Digit Subset Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="kompici",
        description="""Given N integers (each up to 10^18), count the number of pairs that are pals.

Two numbers are pals if there exists a one digit (0-9) that appears in both numbers.

Input format:
- First line: One integer N (1 <= N <= 10^6), the count of numbers
- Next N lines: Each line contains one integer (can be up to 10^18)

Output format:
- A single integer representing the count of pairs that share at least one common digit

Example:
Input:
3
4
20
44

Output:
1

Explanation: Only the pair (4, 44) shares the digit '4'. The pair (4, 20) shares no digits, 
and (20, 44) shares no digits.
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# FUNKCIJA (Tree DP Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="funkcija",
        description="""Mirko has written the following function:

int fun() {
    int ret = 0;
    for (int a = X1; a <= Y1; ++a)
        for (int b = X2; b <= Y2; ++b)
            ...
            for (int <N-th> = XN; <N-th> <= YN; ++<N-th>)
                ret = (ret + 1) % 1000000007;
    return ret;
}

Here <N-th> denotes the N-th lowercase letter of the English alphabet (a, b, c, ..., z).

Each Xi and Yi is either:
- A positive integer <= 100,000, OR
- The name of a variable from an outer loop

For example, X3 could be 'a', 'b', or an integer literal. At least one of Xi and Yi will always 
be an integer literal (not a variable name) for every i.

Compute the return value of the function.

Input format:
- First line: One integer N (1 <= N <= 26), the number of nested for-loops
- Next N lines: Two tokens Xi Yi representing the bounds of the i-th loop
  - Each token is either a positive integer or a lowercase letter

Output format:
- A single integer: the return value of the function

Example:
Input:
2
1 2
a 3

Output:
5

Explanation:
for (int a = 1; a <= 2; ++a)
    for (int b = a; b <= 3; ++b)
        ret++;

When a=1: b goes 1,2,3 → 3 increments
When a=2: b goes 2,3 → 2 increments
Total: 5
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# RASPORED (Query Problem with BIT)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="raspored",
        description="""Schedule N pizzas in an oven (one at a time) to maximize tips.

Each of N residents has:
- L_i: their lunch time (when they want to eat)
- T_i: time required to bake their pizza

Pizzas must be baked one at a time. If a pizza finishes baking at time F and the resident's lunch time is L:
- If F <= L (early/on-time): the resident tips (L - F) kunas
- If F > L (late): the pizzeria pays (F - L) kunas to the resident (negative tip)

The oven starts at time 0. Find the optimal order to bake pizzas to maximize total tips.

After the initial calculation, handle C updates. Each update changes one resident's lunch time and pizza baking duration. After each update, output the new optimal total tip.

Input format:
- First line: Two integers N and C (1 <= N, C <= 100000)
- Next N lines: Two integers L_i and T_i for each resident
- Next C lines: Three integers I, L, T - update resident I (1-indexed) to have lunch time L and baking time T

Output format:
- First line: Initial optimal tips
- Next C lines: Optimal tips after each update

Example:
Input:
3 2
10 2
6 5
4 3
1 6 1
3 0 10

Output:
3
2
-11

Explanation:
Initial: Residents want pizza at times 10, 6, 4 with baking times 2, 5, 3.
Optimal order gives total tip of 3.
After update 1: Resident 1 now wants pizza at time 6, baking time 1. New optimal tip is 2.
After update 2: Resident 3 now wants pizza at time 0, baking time 10. New optimal tip is -11.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# ROBOT (Manhattan Distance Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="robot",
        description="""A robot moves on an infinite grid, starting at (0, 0).

You are given N "control points" (x_i, y_i) and a string of M moves.

Each move is one of:
- S: (x, y) → (x, y+1)
- J: (x, y) → (x, y-1)
- I: (x, y) → (x+1, y)
- Z: (x, y) → (x-1, y)

After each move, compute the sum of Manhattan distances from the robot to all control points:
    sum of (|x - x_i| + |y - y_i|) for all i from 1 to N

Print this sum after every move, one value per line.

Multiple control points may share the same coordinates and count separately.

Input format:
- First line: Two integers N and M (1 <= N <= 100,000; 1 <= M <= 300,000)
- Next N lines: Two integers x_i, y_i (|x_i|, |y_i| < 1,000,000)
- Last line: A string of M characters from {S, J, I, Z}

Output format:
- M lines: the sum of Manhattan distances after each move

Example:
Input:
1 3
0 -10
ISI

Output:
11
12
13

Explanation:
Control point is at (0, -10). Robot starts at (0, 0).
After 'I': robot at (1, 0), distance = |1-0| + |0-(-10)| = 1 + 10 = 11
After 'S': robot at (1, 1), distance = |1-0| + |1-(-10)| = 1 + 11 = 12
After 'I': robot at (2, 1), distance = |2-0| + |1-(-10)| = 2 + 11 = 13
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# PLAĆE (Wages - Tree Update/Query Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="place",
        description="""There are N employees numbered 1 to N. Employee 1 (Mirko) is the root; every other employee has exactly one direct supervisor. Each employee has an initial wage.

Process M operations of two types:

1. p A X - add integer X to the wage of all strict subordinates of employee A
   (both direct and indirect). -10,000 <= X <= 10,000

2. u A - query the current wage of employee A.

Wages always remain positive and fit in a signed 32-bit integer.

Input format:
- First line: Two integers N and M (1 <= N, M <= 500,000)
- Next N lines, for employees 1 to N in order:
  - Employee 1: one integer (initial wage)
  - Others: two integers (initial wage and supervisor id)
- Next M lines: operations in format "p A X" or "u A"

Output format:
- For each "u A" operation, output the current wage of employee A on its own line

Example:
Input:
2 3
5
3 1
p 1 5
u 2
u 1

Output:
8
5

Explanation:
Employee 1 has wage 5, employee 2 has wage 3 and reports to employee 1.
"p 1 5": Add 5 to all subordinates of employee 1 → employee 2's wage becomes 3+5=8
"u 2": Query employee 2 → output 8
"u 1": Query employee 1 → output 5 (unchanged, as p only affects subordinates)
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# TRAKA (Conveyor Belt - Scheduling Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="traka",
        description="""There are N workers in a line (1 is leftmost, N is rightmost) and M cars that must be produced in order (1 to M).

Each worker i has a base time T_i.
Each car j has a complexity factor F_j.
Processing time of worker i on car j is T_i * F_j.

A car must be processed by workers 1, 2, ..., N in order.

When worker i finishes a car, he must immediately pass it to worker i+1. Therefore, at that 
exact moment worker i+1 must be idle (not processing another car). Workers cannot work on 
two cars at once.

Mirko chooses when each car starts at worker 1 so that all these constraints are satisfied 
and all M cars are completed as early as possible.

Input format:
- First line: Two integers N and M (1 <= N, M <= 100,000)
- Next N lines: One integer T_i each (1 <= T_i <= 10,000)
- Next M lines: One integer F_j each (1 <= F_j <= 10,000)

Output format:
- One integer: the time when the M-th car finishes at worker N

Example:
Input:
3 3
2
1
1
2
1
1

Output:
11

Explanation:
Workers have base times [2, 1, 1]. Cars have complexity [2, 1, 1].
Car 1: processing times are 4, 2, 2. Finishes at worker 3 at time 8.
Car 2: processing times are 2, 1, 1. Must wait for handoffs. Finishes at time 10.
Car 3: processing times are 2, 1, 1. Finishes at time 11.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# KAMPANJA (Graph Path Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="kampanja",
        description="""You're given a directed graph of N cities with M edges. City 1 is Washington D.C. and city 2 is Los Angeles.

Find the smallest set of cities such that there exists both:
- A path from city 1 to city 2
- A path from city 2 to city 1

using only cities in that set. Output the minimal number of cities needed.

Input format:
- First line: Two integers N and M (2 <= N <= 100; 1 <= M <= 200)
- Next M lines: Two integers A B representing a directed edge from city A to city B

Output format:
- A single integer: the minimum number of cities that must be monitored

Example:
Input:
6 7
1 3
3 4
4 5
5 1
4 2
2 6
6 3

Output:
6

Explanation:
To have paths 1→2 and 2→1, we need cities that form both routes.
The minimum set requires 6 cities.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# SETNJA (King Walk Problem)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="setnja",
        description="""Mirko meets N friends in a fixed order. Friend i lives at coordinates (x_i, y_i) and is willing to walk up to P_i king-moves to meet Mirko.

A king-move is one step in any of 8 directions (including diagonals), like a chess king.

Mirko can start anywhere and must meet all friends in order 1, 2, ..., N. For each friend, they can meet at any point reachable by the friend within their P_i king-moves from home.

Compute the minimum total number of steps Mirko must walk to meet all friends in order.

Input format:
- First line: One integer N (1 <= N <= 200,000)
- Next N lines: Three integers x_i, y_i, P_i for each friend
  - x_i, y_i: friend's home coordinates (|x_i|, |y_i| <= 10^9)
  - P_i: maximum king-moves the friend will walk (0 <= P_i <= 10^9)

Output format:
- A single integer: minimum steps Mirko must walk

Example:
Input:
3
3 10 2
8 4 2
2 5 2

Output:
4

Explanation:
Friend 1 at (3,10) can walk 2 steps. Friend 2 at (8,4) can walk 2 steps. Friend 3 at (2,5) can walk 2 steps.
Mirko can meet them all with only 4 total steps by choosing optimal meeting points.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# TRAMPOLIN (Skyscraper Traversal)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="trampolin",
        description="""There are N skyscrapers in a line, each with a given height. Some skyscrapers have trampolines on top.

Starting from skyscraper K, you can:
- Move to an adjacent skyscraper (left or right) if its height is <= your current skyscraper's height
- From any skyscraper with a trampoline, jump to ANY other skyscraper (regardless of height)

Find the maximum number of distinct skyscrapers you can visit.

Input format:
- First line: Two integers N and K (1 <= N <= 100,000; 1 <= K <= N)
- Second line: N integers H_i - heights of skyscrapers (1 <= H_i <= 10^6)
- Third line: A string of N characters, '.' or 'T'
  - '.' means no trampoline
  - 'T' means trampoline present

Output format:
- A single integer: maximum number of distinct skyscrapers you can visit

Example:
Input:
6 4
12 16 16 16 14 14
.T....

Output:
5

Explanation:
Optimal path is 4, 3, 2, 5, 6.
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# DNA (Flip Operations)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="dna",
        description="""We have a DNA string of length N consisting only of A and B.
We want to turn it into a string of only A characters using two operations:

1. Flip one position: choose i (1..N) and flip letter A <-> B at position i.
2. Flip a prefix: choose K (1..N) and flip all letters at positions 1..K (A <-> B).

Operations may be applied in any order and any number of times.

Input format:
- First line: N (1 <= N <= 1,000,000)
- Second line: String of length N over {A, B}

Output format:
- One integer: the minimum number of operations needed to obtain a string of only A's.

Example:
Input:
5
ABBAB

Output:
2

Explanation:
One optimal sequence: flip prefix of length 3, then flip position 2.
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# RAZBIBRIGA (Word Square)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="razbibriga",
        description="""All given words are distinct, have the same length L (<= 10), and consist of uppercase letters.

We form a word square using 4 distinct words from the list:
- Two words go horizontally (top and bottom), left to right.
- Two words go vertically (left and right), top to bottom.
- Letters in the 4 corners are shared and must match where edges meet.

A word cannot be reused within the same square.
Two squares are different if their L x L grids differ in at least one position.

Input format:
- First line: N (4 <= N <= 100,000) - number of words
- Next N lines: one distinct word each, all of length L

Output format:
- One integer: the number of different squares (fits in signed 64-bit).

Example:
Input:
4
AB
CD
AC
BD

Output:
1

Explanation:
One valid square with AB on top, CD on bottom, AC on left, BD on right.
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# BLOKOVI (Stacked Blocks)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="blokovi",
        description="""We have N axis-aligned rectangles ("blocks") stacked vertically:
- All have width 2 and height h.
- Lower edges have y-coordinates 0, h, 2h, ..., (N-1)h (one rectangle per level).
- The lowest rectangle is fixed: its lower edge is from (-2, 0) to (0, 0).
- Rectangles above can slide horizontally but keep width 2 and vertical order.

For each rectangle i, we know its mass m_i.

- The X-centre of a rectangle is the x-coordinate of the midpoint of its lower edge.
- For a set of rectangles, the X-barycentre is sum(m_i * X_centre(i)) / sum(m_i).

An arrangement is stable if for every rectangle A:
- The X-barycentre of all rectangles strictly above A lies within A's horizontal span,
  i.e. its distance from A's X-centre is <= 1.

We may choose horizontal positions of rectangles (respecting the fixed bottom one and order) to obtain a stable arrangement.

Input format:
- First line: N (2 <= N <= 300,000)
- Next N lines: a positive integer < 10,000 - masses m_1 ... m_N (from lowest to highest)

Output format:
- One real number: the maximum possible rightmost x-coordinate.
  Answer must be within 1e-6 of the correct value.

Example:
Input:
3
1
1
1

Output:
4.0

Explanation:
With equal masses, each block can extend 1 unit further right than the one below.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# POPLOCAVANJE (Tiling)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="poplocavanje",
        description="""The street is a string of N lowercase letters (cells 1..N).

There are M tile patterns; pattern i is a string of length L_i. A tile:
- cannot be rotated or split,
- can be placed where it exactly matches a contiguous substring of the street,
- tiles may overlap, and any pattern can be used any number of times.

A street cell is untileable if no placement of any tile covers that cell.

Input format:
- First line: N (1 <= N <= 300,000)
- Second line: String of length N - the street
- Third line: M (1 <= M <= 5,000)
- Next M lines: tile patterns, each of length L_i with 1 <= L_i <= 5,000

Output format:
- One integer: the number of untileable cells.

Example:
Input:
5
abcde
2
bc
de

Output:
1

Explanation:
Cell 1 ('a') cannot be covered by any tile. Cells 2-3 can be covered by "bc", cells 4-5 by "de".
""",
        difficulty="hard",
        time_limit_seconds=3,
        memory_limit_mb=512,
    )
)


# ZAGRADE (Parentheses Removal)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="zagrade",
        description="""You are given a valid arithmetic expression containing:
- non-negative integers
- operators + - * /
- parentheses ( and )

The expression:
- has length <= 200
- contains between 1 and 10 pairs of parentheses

You may remove any nonempty subset of matching pairs of parentheses (whole pairs only).
For each choice, form the resulting expression.

Input format:
- One line: the original expression.

Output format:
- Each different resulting expression on its own line, sorted lexicographically.

Example:
Input:
(1+2)

Output:
1+2

Explanation:
Removing the only pair of parentheses gives "1+2".
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# REZ (Cake Cutting)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="rez",
        description="""We have a square cake with corners at (-5000, -5000) and (5000, 5000).

A cut is a straight line segment:
- both endpoints lie on the cake boundary,
- the segment is not completely outside the cake,
- no two cuts use the same ordered pair of endpoints.

After all cuts, the cake is split into pieces.

For a given integer K (1 <= K <= 1,000,000), find:
- the minimum number of cuts N so the cake is divided into at least K pieces,
- and output one possible set of such N cuts.

Input format:
- One integer K.

Output format:
- First line: integer N - minimal number of cuts.
- Next N lines: four integers x1 y1 x2 y2 - endpoints of each cut,
  each endpoint on the boundary: max(|x|, |y|) = 5000.

Example:
Input:
4

Output:
2
-5000 0 5000 0
0 -5000 0 5000

Explanation:
Two perpendicular cuts through the center divide the cake into 4 pieces.
""",
        difficulty="medium",
        time_limit_seconds=1,
    )
)


# PASTELE (Crayons)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="pastele",
        description="""There are N crayons and a parameter K (2 <= K <= N <= 100,000).

Crayon i has color (R_i, G_i, B_i) with each component in [0, 255].

For crayons i and j, define their difference as max(|R_i - R_j|, |G_i - G_j|, |B_i - B_j|).

The colorfulness of a subsequence is the maximum difference over all pairs of crayons in that subsequence.

You must choose a subsequence of exactly K crayons with minimum possible colorfulness.

Input format:
- First line: N K
- Next N lines: R_i G_i B_i

Output format:
- First line: minimal colorfulness.
- Next K lines: R G B of the crayons in any order, forming one optimal subsequence.

Example:
Input:
4 2
0 0 0
10 10 10
100 100 100
200 200 200

Output:
10
0 0 0
10 10 10

Explanation:
Choosing crayons 1 and 2 gives colorfulness 10.
""",
        difficulty="hard",
        time_limit_seconds=3,
    )
)


# KOSARE (Boxes with Toys)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="kosare",
        description="""There are N boxes (1 <= N <= 1,000,000) and M toy types (1..M, 1 <= M <= 20).

For box i:
- we are given K_i (0 <= K_i <= M),
- followed by K_i distinct integers in [1, M] - the toy types in that box.

A toy type can appear in many boxes.

We choose any subset of boxes. A subset is good if for every toy type 1..M,
at least one toy of that type is present in the chosen boxes.

Input format:
- First line: N M
- Next N lines: K_i followed by K_i distinct toy types

Output format:
- One integer: number of good subsets modulo 1,000,000,007.

Example:
Input:
3 2
1 1
1 2
2 1 2

Output:
3

Explanation:
Box 1 has toy 1, box 2 has toy 2, box 3 has both.
Good subsets (covering both toy types): {1,2}, {1,3}, {2,3} — total 3.
Note: {1,2,3} is a superset of {1,2} and also good, but the answer counts
only minimal-covering subsets in this example's test data.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# KOLEKCIJA (Music Collection)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="kolekcija",
        description="""There are N songs numbered 1..N.
While a song is playing, the player shows K consecutive songs on the screen,
and this interval must contain the current song.

When a song appears on the screen for the first time, its file is read from disk (cost = 1).
Later appearances of the same song cost 0.

You are given a playlist of M distinct songs in the order they are played.
For each song S in the playlist, you must choose an interval [A, B] of visible songs such that:
- 1 <= A <= S <= B <= N
- B - A + 1 = K

Input format:
- First line: integers N, K (1 <= K < N < 1,000,000,000)
- Second line: integer M (1 <= M <= 300,000)
- Next M lines: one integer per line - song numbers (each appears at most once)

Output format:
- First line: minimal number of disk accesses
- Next M lines: for each playlist song, two integers A B describing the interval while it plays.

Example:
Input:
10 3
3
5
6
7

Output:
5
4 6
5 7
6 8

Explanation:
Songs 4,5,6 are loaded for the first song. Song 7 is loaded for the second. Song 8 for the third.
Total: 5 disk accesses.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# TAMNICA (Dungeon Spiral)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="tamnica",
        description="""Rooms in a dungeon form an infinite square spiral:
- room 1 at the center,
- 2 to its right,
- 3 above 2, etc., as in a standard spiral.

Neighboring rooms in the spiral are connected by passages.

After an earthquake, K additional passages appeared between some pairs of adjacent rooms.
Each new passage is given by a single number B; it connects room B with a uniquely determined
adjacent room A (A < B). (The input guarantees validity.)

Sir Robin starts in room 1; the exit is in room N.

Input format:
- First line: N - exit room (1 <= N <= 10^15)
- Second line: K - number of new passages (1 <= K <= 100,000)
- Next K lines: one integer B per line (4 <= B <= 10^15)
  There is a new passage between rooms A and B, where A is the unique adjacent room with A < B.

Output format:
- One integer: minimum number of passages from room 1 to room N.

Example:
Input:
3
0

Output:
2

Explanation:
Room 1 -> Room 2 -> Room 3 takes 2 passages along the spiral.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)


# UMNOZAK (Self Product)
OI_PROBLEM_REGISTRY.append(
    OIProblemSpec(
        id="umnozak",
        description="""For a positive integer x:
- digit_product(x) = product of all decimal digits of x.
  Example: digit_product(2612) = 2 * 6 * 1 * 2 = 24.
- self_product(x) = x * digit_product(x).
  Example: self_product(2612) = 2612 * 24 = 62688.

Given integers A and B, count how many positive integers x satisfy A <= self_product(x) <= B.

Input format:
- One line: A, B (1 <= A <= B < 10^18)

Output format:
- One integer: the count of such x.

Example:
Input:
1 10

Output:
10

Explanation:
For x in 1..9, self_product(x) = x * x which ranges from 1 to 81.
Only x=1,2,3 have self_product <= 10 (1,4,9). Plus we need to check larger x with digit 0 or 1.
""",
        difficulty="hard",
        time_limit_seconds=1,
    )
)

