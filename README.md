# async-sqlite-server
 
## Built with FastAPI, served with Hypercorn, and fed with aiosqlite

- [x] Fully asynchronous server/database backend
- [x] Flexible "turing complete" configuration
- [x] HTTP3/QUIC support
- [ ] Non-blocking IPC transport
- [ ] Available as pypi package
- [ ] User dependency injection

## How it works
- Utilizes database file "routers", minimally, key/value databases, which route generated UUIDs to specific database paths, instead of limited structure directory naming
- Database router files stay connected to reduce overhead from repeatedly connecting to one
- On startup, it scans for config and most importantly, `meta.yaml`, which dictates most configuration
- You can write your own database schemas as simple .yaml files which get generated into sqlite databases
- I have not made pre-written endpoints for database functions but will provide them in the config for the next release. I also made some dumb changes to how responses are crafted but its not like people will use this for now :)
- To make endpoints, you can use `meta.yaml`, it is pretty straightforward and you can follow the sample `meta.yaml` shipped with the release
- Its very fast, the main libraries used are all performance oriented

Its not much at the moment, but theres lots more features to come! I will update it about every other week when i have time to work on it
