# Part 2: teaching the computer to read a spreadsheet

## The idea in one line

We taught the code to spot which cells "talk to" which other cells — so later we can catch *one* mistake instead of blaming a student for every cell it touches.

## Show, don't tell

Our test sheet has this:

```
F3:  =SUM(B3:E3)      <- "Total" column
B5:  =B3-B4           <- "Profit" row
```

F3 reads B3, C3, D3, E3. B5 reads B3 and B4. We just wrote that down as a little map:

```
F3 -> B3, C3, D3, E3
B5 -> B3, B4
```

That map is called a **dependency graph**. Nothing fancier than "who reads from whom."

## Why bother

Say a student typos their Revenue number (B3). Their Profit formula (`=B3-B4`) is *written correctly* — it's just fed a bad number.

- **Without the map:** the grader sees "Profit is wrong" and dings it.
- **With the map:** the grader traces Profit back to B3, sees the formula itself was fine, and docks points once — at B3, where the actual mistake is.

That's the whole point of this project's "grade the method, not just the number" promise. This part built the map. A later part (19) will do the walking-backward.

## One decision, quickly

The formula stays stored as plain text (`"=SUM(B3:E3)"`) for now, not broken down into pieces. Good enough for spotting cell references. Not good enough to know that `=A1+A2` and `=SUM(A1:A2)` are secretly the same calculation — that needs the text properly parsed, which is a hand-write exercise you do later, so we're not duplicating that work now.

## One loose thread

Formula cells came back with no "last known answer" cached — because our test file was machine-generated, and only real Excel calculates and caches formula results. Real student files will have this; we're not relying on it being trustworthy yet. Parked, not forgotten.

---

## Your turn

1. Using B5 (`=B3-B4`), explain the dependency map in your own words.
2. B3 has a typo, B5's formula is correct. Walk through how the map saves B5 from losing points.
3. What breaks if we skip the map and just compare final values cell-by-cell?
