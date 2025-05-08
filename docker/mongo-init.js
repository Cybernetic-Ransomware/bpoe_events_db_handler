const appDB = process.env.MONGO_DB;
const appCollection = process.env.MONGO_COLLECTION;

db = db.getSiblingDB(appDB);

if (appCollection) {
  const collections = db.getCollectionNames();
  if (collections.indexOf(appCollection) == -1) {
      db.createCollection(appCollection);
      print(`Collection '${appCollection}' created successfully in database '${appDB}'.`);
  } else {
      print(`Collection '${appCollection}' already exists in database '${appDB}'.`);
  }
}