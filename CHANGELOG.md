# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [0.1] - 2017-02-11
### Added
- Web application via Flask and SQLAlchemy
- Simple extensibility with discovery via entrypoints and extension
via calling hooks
- Basic user login/logout via GitHub OAuth
- Custom roles assigned to users (special admin role)
- Public pages for users, organizations and repositories
- Fulltext search for users, organizations and repositories
- Managing own (only personal) GitHub repositories within app
- Listening for webhooks (push, release, repository) and storing information
about repositories to the database
- Repository within app can be public, private or hidden (secret URL)
- Administrator can manage users, repositories, roles and extensions
within administration zone
- Very simple REST API (GET only) via flask-restless
- Commands to create DB, assign role and check/process new repository events
