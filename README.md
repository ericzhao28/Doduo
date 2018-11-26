# Doduo: dependency tree matching.
A service for matching natural language queries against dependency tree patterns.
Doduo also supports advanced slotting functionality for argument parsing natural
language queries.

![license](https://img.shields.io/github/license/mashape/apistatus.svg)
[![Maintenance Intended](http://maintained.tech/badge.svg)](http://maintained.tech/) 

Doduo serves a basic [Flask API](https://www.flaskapi.org/#overview) that consumes natural language sentences and returns
pattern matches and any slot values. See Usage for detailed API specifications. Dependency tree patterns are
defined in the `config/` folder as [YAML](https://pyyaml.org/wiki/PyYAML) files. There, users can configure a set of
"templates" for the Doduo engine to match incoming queries against. In a chatbot application, each template corresponds
to an intent. The underlying dependency parsing, part-of-sentence tagging (POS) and named-entity-recogntition (NER)
functionality are provided through the [Spacy](https://github.com/explosion/spaCy) library.

# Usage
First, install the [Numberbatch word embedding models](https://github.com/commonsense/conceptnet-numberbatch#downloads)
into `Doduo/dumps/numberbatch-en-17.06.txt.gz`- specifically install the non-binary, gunzipped 17.06 model.
Then modify `Doduo/Doduo/config.py` to point to your desired config. It is by default set to point to the
beer chatbot sample. Doduo comes Dockerized so simply build the Docker container and run:
```
docker build -t doduo_example:latest .
docker run -d -p 5000:5000 doduo_example
```
If you're running Doduo outside of Docker, you'll need Python 3.6 installed with Spacy and the other
pip packages listed in `requirements.txt`. See the `Dockerfile` for approximate installation steps.

## API
The server will be available at `localhost:5000`/`0.0.0.0:5000`. Make a POST request to `${LOCALHOST}:5000/match`
with the JSON body: `{"query": "...", "templates": []}`. The templates attribute is optional- if specified, the
engine will only compare the query against those template names. `query` should be a natural language
string- multi-sentence is supported.
Upon success, the response body looks like:
```
{"success": True,
 "error": None,
 "matched": [
    {"template1": {},
     "template3": {"slot1": ["General Kenobi"]},
     "__alternatives__": {},
     "__sentence__": "Hello there General Kenobi"}
 ]
}
```

The `matched` keys stores the result of the "match". The value for `matched` is a list of dictionaries, each
corresponding to a sentence in the query. While the dictionaries are returned in the natural order of
the sentences, the precise sentence value can be found in `__sentence__`. The rest of the keys correspond
to "matches" for templates. In the above example, the sentence "Hello there General Kenobi" matches the
`template1` and `template3` patterns. In the case of template3, we are provided slot values resulting from
argument-parsing.

## Sample application
Doduo includes a sample application for a beer chatbot. The config file `configs/beer.yml` looks like:
```
attribute_question:
  patterns:
    - exact_match: ["is", "are"]
      children:
        - slot_name: "attribute"
          rels: ["nsubj"]
          pos_match: ["noun"]
          children:
            - rels: ["det"]
              pos_match: ["adj"]
              exact_match: ["which", "what"]
        - slot_name: "product"
          rels: ["attr"]
          pos_match: ["noun"]
          slot_is_full_phrase: True

action_request:
  patterns:
    - slot_name: "action"
      pos_match: ["verb"]
      children:
        - exact_match: ["do", "can"]
          rels: ["aux"]
          pos_match: ["verb"]
        - exact_match: ["you"]
          rels: ["nsubj"]
        - slot_name: "product"
          pos_match: ["noun"]
          rels: ["dobj"]
          slot_is_full_phrase: True

preference_statement:
  patterns:
    - slot_name: "opinion"
      pos_match: ["verb"]
      soft_match: ["hate", "love", "drink", "disgusting"]
      children:
        - slot_name: "opinion negation"
          rels: ["neg"]
          optional: True
        - exact_match: ["I", "we"]
          rels: ["nsubj"]
        - slot_name: "product"
          pos_match: ["noun"]
          rels: ["dobj"]
          slot_is_full_phrase: True
```
Here, we match against 3 templates: each one corresponds to an intent.
The `attribute_question` template matches phrases including "What flavor is the stout?".
The `action_request` template matches phrases including "Do you recommend any ales?".
The `preference_statement` template matches phrases including "I don't drink chocolate ale."

Let's test "Do you recommend any winter stouts" on the sample application.
The dependency parse of the sentence looks like:
![Dependency tree](assets/recommend_stouts.png?raw=true "Do you recommend any winter stouts?")

The request looks like:
```
curl -X POST \
  http://localhost:5000/match \
  -H 'cache-control: no-cache' \
  -H 'content-type: application/json' \
  -d '{"query": "Do you recommend any winter stouts?"}'
```
You should receive the following response:
```
{"success": True,
 "error": None,
 "matched": [
    {"action_request": {"action": ["recommend"], "product": ["any winter stouts"]},
     "__sentence__": "Do you recommend any winter stouts?",
     "__alternatives__": {}}
 ]
}
```

# Writing templates
Template configurations are all defined under `Doduo/configs/`. A sample configuration for a beer
chatbot app is included under `Doduo/configs/beer.yml`.

## Overview
Each natural language template is defined as a set of "patterns". If an incoming query matches
any one of the patterns, it is considered to have "matched" the template.
```
hello_there:
  patterns:
    - ...
    - ...
    - ...
```
Each pattern will be compared against the dependency parse tree of the incoming queries.
These patterns are defined as a tree:
```
hello_there:
  patterns:
    - exact_match: ["friend", "enemy"]
      children:
        - exact_match: ["hello", "hi", "hey"]
          rels: ["intj", "attr"]
```
In this example, we will match any query with a dependency tree containing either the word "friend" or "enemy",
with a dependency child corresponding to one of the words "hello", "hi" or "hey". The `exact_match` key indicates
that for a word to match this part of the pattern, it must be one of the listed options (in this case,
"friend" or "enemy"). We also enforce that the child must be related to the parent through either the
"intj" or the "attr" relationship- this is specified through the `rels` key attached to the child. 
By default, children must be matched for a pattern to be matched. In other words, while "hello friend" matches this
template, "friend" alone will not. This behavior can be modified by adding an `optional: True` flag:
```
hello_there:
  patterns:
    - exact_match: ["friend", "enemy"]
      children:
        - exact_match: ["hello", "hi", "hey"]
          optional: False
          rels: ["intj", "attr"]
```

## Matching options
As shown above, query words will be matched against the example's vertices using an "exact" match. We also provide options
for either matching against the part of sentence `pos_match`, the NER tag `ner_match`, and soft matches `soft_match`.
The latter can only be used on common vocabulary as the matcher will check a variable radius around the provided examples'
word embeddings.
```
- exact_match: ["color"]
  soft_match: ["price"]
  pos_match: ["noun"]
  ner_match: ["PERSON"]
```
This pattern will match any word exactly matching "color" OR somewhat matching "price" OR that is a noun OR that is a
person's name. By default, all matches are case insensitive. To disable this, add the `case_sensitive: True` flag.
If a `rels` list is provided, a word's dependency parse relationship to its parent must be in the `rels`
list for a match to be successful. In other words, the word "hello" will only match the below pattern
if it is related to its parent through the "intj" or "attr" relation.
```
- exact_match: ["hello", "hi", "hey"]
  rels: ["intj", "attr"]
```

## NER/POS matcing
The list of legal options for `pos_match` is:
```
ADJ: adjective
ADP: adposition
ADV: adverb
AUX: auxiliary verb
CONJ: coordinating conjunction
DET: determiner
INTJ: interjection
NOUN: noun
NUM: numeral
PART: particle
PRON: pronoun
PROPN: proper noun
PUNCT: punctuation
SCONJ: subordinating conjunction
SYM: symbol
VERB: verb
X: other
```
This corresponds to the [Universal POS Tag Set](http://universaldependencies.org/en/pos/index.html) and Spacy's `token.pos_` tags.
The legal options for `ner_match` are exactly the possible [Spacy NER classes](https://spacy.io/api/annotation#named-entities).

## Slot-filling
Slot-filling functionality is provided through the "slot_name" attribute. When a query matches a template with a slot,
the words in the query that match with the subtree marked with a "slot_name" will be returned in a dictionary of
form: {"slot_name_1": ["..."], "slot_name_2": ["..."]}. For example:
```
hello_there:
  patterns:
    - slot_name: "mentioned_name"
      ner_match: ["PERSON"]
      children:
        - exact_match: ["hello", "goodbye"]
          rels: ["INTJ"]
```
In this example, the subtree vertex corresponding to the $NAME variable in "hello ${NAME}" is returned in the
form `{"mentioned_name": ["Brian Liang"]}`.

If there are multiple matching slot values for a given pattern, alternative slot value interpretations and provided through the `__alternatives__` slot value.
The ordering of slot priorities is determined by the ordering of the config file. Using the above
 example config, the query "Hello Brian and Hello Eric and Hello Alex" would result in a response body of:
```
{"success": True,
 "error": None,
 "matched": [
    {"hello_there":{"mentioned_name": ["Brian"]},
     "__sentence__": "Hello Brian and Hello Eric and Hello Alex",
     "__alternatives__": {"hello_there": [{"mentioned_name": ["Eric"]},
                                          {"mentioned_name": ["Alex"]}]}
 ]
}
```

If the same `slot_name` value is used in mutltiple places, slot values will all be returned in the same list.
For example, the below config would result in `{"mentioned_name": ["hello", "Brian"]}` for "hello Brian".
```
hello_there:
  patterns:
    - slot_name: "mentioned_name"
      ner_match: ["PERSON"]
      children:
        - slot_name: "mentioned_name"
          exact_match: ["hello", "goodbye"]
          rels: ["INTJ"]
```
This is why slot values are actually lists.

Note that if the resulting pattern is compound, the slot will use
the full compound phrase unless `slot_is_not_compound: True` is provided.
Alternatively, if you'd like the slot to return all neighboring words that are downstream in the parse tree,
provide `slot_is_full_phrase: True`.

# License
Copyright 2018 Eric Zhao

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
