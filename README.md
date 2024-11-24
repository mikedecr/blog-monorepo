# Blog MonoRepo

A repository for holding all blog posts written under the `mikedecr` (professional) handle.


## Structure:

Posts contained here may be...

- plain text posts that don't need a special computing environment
- submodules for richer posts that specify their own computational dependencies


## Presenting the blog on a website

This repository supersedes an earlier model in which [every blog post was a direct submodule to the website](https://github.com/mikedecr/post_blogdown-submodules/blob/5c7dbcc11ee81621558c4b680d374b618d4003df/index.qmd#L111-L122).
This granular model got the big points right:

- **Posts are independent.**
  I don't need to version-control the development of one post in the same conceptual space as any other post.
  And the website might want to display some posts but not others.
- **Decouple the computational environments of separate posts.**
  The only computational environment that a post should be responsible for is _its own_.
  If post X requires some package, post Y should never care.
  In principle this applies not just to the "literate programming" dependencies (like R package libraries, or Python package environments) but also the tools that render a blog post into its output (Rmarkdown / blogdown, Quarto, Jupytext, or any other document rendering system).
- **The website should be agnostic to all computational environments**.
  Posts don't care about each other's environments, and neither should the website care about a "union" environment to maintain all posts.
  The website really only needs to (a) move files around so that it can correctly (b) trigger the website build command.

But the granular model gets some things wrong too.
It believes that the blog posts should be provided _to the website_ as separate modules rather than through one omnibus "blog" monorepo module.
I wrote about this [here](https://github.com/mikedecr/post_blogdown-submodules/blob/5c7dbcc11ee81621558c4b680d374b618d4003df/index.qmd#L280-L296).
In short, sometimes the website requires the output to be organized in ways that the content source should not have to care about, and we don't want to couple the blog source to the surrounding context.
So even though handling many blog post repositories separately is tedious and repetitive, this constaint stood on good principle.

But I no longer believe this is a real constraint.
We can just import the blog source in one location, and use some scripting at the website layer to build and move/link blog files wherever they need to go.
The source stays the source, and the website handles what it needs.
Even in the extreme cases where we might need to inject new metadata into the rendered output (!) we can just handle this with a well-defined scripting routine at the website layer.

Basically if the website imposes additional constraints on the source, then those constraints must be rule-based and thus can be handled programmatically.
Let the computer handle it.


## Abstract requirements

Done correctly, any post can be a member of the blog monorepo as long as it has:

- source files that are enough to generate markdown output when built
- a build routine that we can invoke

For now, we can get away with an assumption that the computational environment is built from the "conda family" and that build routine is basically `conda run -p path/to/env quarto render path/to/index.qmd`
More generally we could defer all responsibility for building to makefiles and abstract away those details completely.
At that point, the only shared assumptions between the blog code and the surrounding website are availability of `make` and the awareness to use it.
