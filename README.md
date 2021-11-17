Static page generator for [defgsus.github.io](https://defgsus.github.io/)


To publish the latest repo index:

    rm cache/repo_list.json
    python src/download.py

And then update the `templates/repo-infos.yaml` and

    python src/render.py


