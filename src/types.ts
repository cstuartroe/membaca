import { User, Language } from "./models";

export type UserState = {
    user: User | null,
    current_language: Language | null,
}