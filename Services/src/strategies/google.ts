// import passport from "passport";
// import { Strategy as GoogleStrategy } from "passport-google-oauth20";
// import { User } from "../models/User";

// passport.use(
//   new GoogleStrategy({
//     clientID: process.env.GOOGLE_CLIENT_ID!,
//     clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
//     callbackURL: "/api/auth/google/callback",
//   }, async (accessToken, refreshToken, profile, done) => {
//     const existing = await User.findOne({ email: profile.emails?.[0].value });
//     if (existing) return done(null, existing);

//     const user = await User.create({
//       email: profile.emails?.[0].value,
//       name: profile.displayName,
//       provider: "google",
//     });
//     done(null, user);
//   })
// );
