This are coding pratices for Juri's vibecoding projects.
My name is Juri, and I really know only Python. You can use other languages, but let's limit those to a bare minimum.
I like well-documented code (both at the beginning of the file and in each method).
When I code, I want to make sure the future me can navigate through it, so I prefer many small,
meaningful files organized in a library subfolder rather than a single BIG file with 100 methods.

Maintainability is key to me, so I prefer code that I can someday put my hands on without having an AI explain to me what it does.

* I love markdown, so try to make files markdown compliant.
* I love colors, so make stdout colorful and emoji-ful.
* I work for Google Cloud, so my cloud of choice is GCP, and Gemini is my LLM of choice.

## github

The code is under github.

## This repo

This is a single repo with a single project. 
* Please keep the README.md up to date with the latest information.
* AI_braindump.md is a file where you dump my thoughts and ideas.
* The file requirements.md contains the basic requirements of the projects we are building, please consider it as a living document.
* project_timeline.md is a file where you dump the timeline of the project: each time we implement a new feature, we add a new line to the timeline and explain the outcome and what's left.
* a `.env` file for environment variables, some of which are to be kept secret. This shall be git-ignored.
* a `.env.dist` file to check into source control and to showcase the environment variables that are needed, with foo values and rich comments.



```bash
$ tree -L 1
├── README.md
├── GEMINI.md
├── Requirements.md
├── AI_braindump.md
├── project_timeline.md
├── .env
├── .env.dist
```

## Feedback loop

This is my vibecoding main project on GitHub.

1. Since I might invoke Gemini help multiple times, make sure to understand the context in `GEMINI.md` on a per-project basis. For instance, if it tells you to 'add function a,b' and you see functions a,b,c, **do not** delete `c`. Most likely there's an undocumented reason why we did so.

2. Since I code across multiple computers (Mac and Linux, mostly), ensure there is an `AI_braindump.md` under each folder to make sure the future you (AI) can read and stay up-to-date. When loading a project under folder X (e.g., `vibecheck/`), make sure to load/read both `GEMINI.md` and `AI_braindump.md`. Keep in mind the difference:
    * `GEMINI.md` for Riccardo to instruct you (AI)
    * `AI_REASONING.md` for you to dump your thoughts across installations. Say you're in the middle of something, or you took a decision about something, dump it there.
    * a `README.md` for any other user to immediately understand:
        * How to use the software
        * How to install the software
        * What it does
        * How to deploy (if it makes sense)
    * Keep `README.md` current with the latest features and installation instructions.



## Testing

Testing should be fast and meaningful. Create a python script to run the tests, and you should occasionally check if you broke something.
And if you know something is broken but tests are not there, please write a test for that functionality, unless you know we're going to dismiss that functionality soon.

## Caching

Since invoking LLMs and doing some other jobs (e.g., finding large files in a filesystem) can be long and tedious, try to implement a caching mechanism sooner rather than later. I like my cache to be under a `.cache/` folder in a plausible and documented location (under this git repo or under the user's home directory): whatever you want, as long as you document it. The cache should have a reasonable default; when in doubt, keep it for one day. This default should be overridable on a per-invocation basis.

## Secrets

I'll keep all secrets in a `.env` file which is NOT under version control. Make sure all needed environment variables are listed in a `.env.dist` file (which is under version control) for documentation purposes.

* Let's use Secret Manager to store all of our secrets.

## LLM

Use python to call LLMs unless otherwise specified or critically needed. 

Do not use the SERPAPI_API unless required; it's expensive.

### python

1. If you use Python, use `uv` and `google-adk` (v1.0 or more) for LLM agents with search function calling.

If using the Python library, make sure to use the Vertex AI (not API KEY) version, since the quota is usually better.
Check the config in `~/git/vibecoding/.env`, and make sure `GOOGLE_CLOUD_PROJECT` is set.
```
export GOOGLE_GENAI_USE_VERTEXAI=true
```

For LLM, it's best to use Python and `google-adk`.
* tutorial to get started: https://google.github.io/adk-docs/tutorials/agent-team/
* For function calling, read docs in https://google.github.io/adk-docs/tools/built-in-tools/
* For MCP: https://google.github.io/adk-docs/tools/mcp-tools/
* For deployment to Cloud Run use https://google.github.io/adk-docs/deploy/cloud-run/ (but beware, we might want to
  do Cloud Run our way, as I've explained above).

Try to add `LLM evaluation` to understand if we are writing good code or good prompts:

* https://google.github.io/adk-docs/evaluate/


## Bugs

* `BUG001` You have a tendency of doing git commit -m "feat: blah `filename`: updated ..".  Stop doing it! Either use single quotes or stop using backticks inside a double-quoted bash string!

## Quality

* use `gitleaks detect -v` and `markdownlint` for ensuring MD quality and no secrets are around.

## Documentation

Ensure every README.md (except thhe root one) has a "📁 Project Structure" H2 chapter, containing a tree-view of hte subfolder, in the style of `tree`. You can actually run `tree` but make sure to prune all irrelevant files, git ignored, irrelevant assets (like images, ...). It needs to be short enough to provide humans with a good understanding of the CODE structure.


Amazing Example:

```markdown
my-project/
├── backend/
│   ├── src/                  # Main backend source code
│   ├── venv/                 # Python virtual environment (ignored by git)
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── requirements.txt
│   ├── run.sh
│   └── ...
├── frontend/
│   ├── src/                  # React components, routes, utils
│   ├── public/               # Static assets (images, logo, etc.)
│   ├── package.json
│   ├── vite.config.js
│   └── ...
├── server/                   # Additional backend services & agents
│   └── ...
├── README.md
└── ...
```
