# Step 2 report: benign pool

| Filter step | Rows left |
|---|---|
| Source file | 701528 |
| Non-empty text after cleaning | 700535 |
| 15-300 words | 413469 |
| Looks English | 409009 |
| Exact/near-exact duplicates removed | 404439 |
| One review per user per product | 404287 |
| Products with at least 20 clean reviews | 3206 products |

## Result

| Item | Value |
|---|---|
| Products selected | 100 |
| Reviews in main pool | 2000 |
| Hard-benign in main pool | 18 (0.9%) |
| Extra hard-benign reviews | 300 |
| Hard-benign rate in all clean reviews | 0.8% |
| Median words per review (main pool) | 36 |

Rating distribution (main pool):

| Rating | Count |
|---|---|
| 1 | 276 |
| 2 | 147 |
| 3 | 181 |
| 4 | 290 |
| 5 | 1106 |

How often each hard-benign signal appears in all clean reviews:

| Signal | Share of clean reviews |
|---|---|
| ignore_word | 0.1% |
| url | 0.0% |
| meta_word | 1.9% |
| imperative_start | 3.2% |
| you_modal | 1.7% |
| long_quote | 0.7% |
| caps_run | 1.5% |

Ten hard-benign examples (check these look instruction-like but harmless):

- [imperative_start;you_modal] I like this DMSO product because it doesn't stink so bad. I use it in combination with another aloe vera pain relieving gel and it works. When using any DMSO product you must use care to wash and rinse your hands and the area of application well prior to use. 
- [meta_word;imperative_start;long_quote] I buy a lot from Amazon but write few reviews. I have to be either delighted or very disappointed to be motivated. In this case, sadly, it’s the latter. Please note that it applies specifically to one print: “Psychedelic” For the price you can get a dozen or t
- [imperative_start;you_modal] Vacuum works great, it works with and without the cord, and it is easy to use. I highly recommend it to anyone! Edit: after several use, I saw that actually this is not a good product at all. First of all, you can easily change the size adjustment during the u
- [meta_word;caps_run] I gave this product 5 because it performs as expected, delivery prompt, and is exactly what the description claims... I USE THIS PRODUCT because...Dang, nothing cleans a floor corner better than these little things! (It cleans many other hard to reach areas, a
- [imperative_start;you_modal] I was suspicious of this cleaner because all I saw about its function was just to rapidly rotate makeup brushes on a liquid soap that it doesn't provide. But it turns out this machine cleans my brushes so thoroughly and quickly. For only 10 seconds of the high
- [you_modal;caps_run] I personally don't like grey hair. So all other products I have tried irritated my skin to the point that I could not use them that was until I found this!! Great product gentle on the skin BUT the process takes me much longer I need to use the organic base fi
- [meta_word;imperative_start] Don't be fooled by other brands...some are yucky! This brand has a nice, mild minty taste and works well if directions are followed.
- [you_modal;long_quote] This is a great concept and I wanted this to work for me. I wanted to have a “Dr. Pimplepopper” moment where I saw my blackheads getting sucked out of their little crevices. It just didn’t happen. I did pause and ask myself if maybe the issue is I don’t have a
- [meta_word;imperative_start] This worked well for me. I have shoulder length very thick wavy hair that has been bleached and re bleached and colored over. My hair was feeling beyond straw. Although damaged I could also tell it just really needed some protein and it would come back to life
- [meta_word;you_modal;caps_run] Love these pencils. NOT SHARP LINES! Soft, creamy yet clear lines. Smudgable. Sets and stays with powder, setting spray. .I can get fine enough line to draw in brows or put a soft wash of background brow shade before you draw the hairs this will smudges beauti