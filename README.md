# text_diff_vis
A non-LLM-powered visualizer of subtle differences in very similar texts.

This is a small stand-alone code that uses Python Standard Library modules to solve a simple problem:

Given two very similar blocks of text, show how the texts differ.

This code was built to solve the problem of detecting, from a periodic longitudinal survey of project managers, changes in a project's scope or objectives.  Normally one would go first to some kind of heavy NLP/LLM solution but in this situation the problem was simplified by a basic human characteristic--laziness!  The survey in question was probably viewed by the project managers it targeted as a nuissance, and, as such, something best answered with boilerplate copy/paste responses to the free text questions on the survey.  That said, most people are conscientious enough to modify boilerplate responses when circumstances change.  If one has the _history_ of the responses, one can align them and compare the tokens (in this case words) in the responses, and, if there are multiple responses, watch the "mutations" in the text unfold over time.

The source code here uses

The module defines functions and a coloring object that can be used in other applications.  It has a built-in test example that can be invoked from the command line to execute a simple example.

```python text_diff_vis.py```

This will process two specimen blocks of text:

```
text1 = """Citizens!  The government regrets to announce that the chocolate 
           ration has been decreased from 50g/day to 25g/day."""
text2 = """Citizens!  The government is pleased to announce that the chocolate 
           ration has been increased from 50g/day to 25g/day.  Doubleplusgood!"""
```

And will yield the merged, highlighted text showing (sadly Github is recalcitrant regarding colors in markdown/HTML so you won't see them on this page!)

* Words common to the original and new texts in <span style="color:yellow;">YELLOW.</span>
* Deleted words from the original text in <span style="color:red;">RED.</span>
* Inserted words from the new text in <span style="color:green;">GREEN.</span>

Applying this logic to the two sample texts yields:

<span style="color:yellow;">Citizens The government</span> <span style="color:red;">regrets</span> <span style="color:green;">is pleased</span> <span style="color:yellow;">to announce that the chocolate ration has been</span> <span style="color:red;">decreased</span> <span style="color:green;">increased</span> <span style="color:yellow;">from 50g/day to 25g/day</span> <span style="color:green;">Doubleplusgood</span>

The punctuation gets stripped in the current version but the tool does its job.
