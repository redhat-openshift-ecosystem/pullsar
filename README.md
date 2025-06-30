# Pullsar

The Pullsar is a Python-based project that aims to make usage stats data
for Openshift operators easily accessible to the users.

It consists of Python scripts that:
- parse operator catalogs to access useful metadata about all mentioned operators and their versions
- use the metadata to identify Quay.io repositories with respective container images
- scan these repositories for usage logs, process them to retrieve pull counts for each operator
- store resulting data in a database for easy access in the future

## License
This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.
