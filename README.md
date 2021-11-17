Static page generator for [defgsus.github.io](https://defgsus.github.io/)


To publish the latest repo index:

    rm cache/repo_list.json
    rm -r cache/commits/last

    python src/download.py

Then update the `templates/repo-infos.yaml` if required and

    python src/render.py

