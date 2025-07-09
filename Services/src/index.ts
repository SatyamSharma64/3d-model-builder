import dotenv from "dotenv";
dotenv.config();

import app from "./app";
import { connectDB } from "./config/db";
import passport from "passport";

const PORT = process.env.PORT || 4000;
app.use(passport.initialize());

connectDB().then(() => {
  app.listen(PORT, () => console.log(`User service running on port ${PORT}`));
});
