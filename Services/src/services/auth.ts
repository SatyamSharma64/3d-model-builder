import jwt from "jsonwebtoken";
import bcrypt from "bcryptjs";

export const generateSalt = bcrypt.genSalt(10);
export const hashPassword = (plain:string, salt:string) => bcrypt.hash(plain,salt);

export const comparePassword = (plain: string, hash: string) => bcrypt.compare(plain, hash);

export const generateToken = (userId: string) => {
    return jwt.sign({userId}, process.env.JWT_SECRET!, { expiresIn: "7d"});
};