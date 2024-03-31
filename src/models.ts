export type User = {
  id: number,
  is_superuser: boolean,
  username: string,
  email: string,
  is_active: boolean,
  date_joined: string,
}

export type Language = {
  id: number,
  name: string,
}

export type Lemma = {
  id: number,
  language_id: number,
  citation_form: string,
  translation: string,
}

export type Document = {
  id: number,
  title: string,
  link: string,
  language: number,
  sentences?: Sentence[],
}

export type Sentence = {
  id: number,
  text: string,
  translation: string,
}

export type Substring = {
  start: number,
  end: number,
}

export type WordInSentence = {
  id: number,
  sentence_id: number,
  lemma_id: number | null,
  substrings: Substring[],
}

export type TrialType = "ct" | "cc" | "cz" | "show";

type Trial = {
  trial_type: TrialType,
  easiness: number,
}

export type CardDescriptor = {
  lemma_id: number,
  due_date: Date,
  last_trial: null | Trial,
}
