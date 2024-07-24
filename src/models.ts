export type User = {
  id: number,
  is_superuser: boolean,
  username: string,
  email: string,
  is_active: boolean,
  date_joined: string,
}

export const LANGUAGE_NAMES = [
    "Dutch",
    "Indonesian",
    "Esperanto",
    "Greek",
    "Russian",
    "Turkish",
] as const;

export type LanguageName = (typeof LANGUAGE_NAMES)[number];

export type Language = {
  id: number,
  name: LanguageName,
}

export type Lemma = {
  id: number,
  language_id: number,
  citation_form: string,
  translation: string,
  metadata: {[key: string]: string},
}

export type Collection = {
  id: number,
  title: string,
  language_id: number,
}

export type Document = {
  id: number,
  title: string,
  link: string,
  collection_id: number,
  sentences?: Sentence[],
}

export type FormatLevel = "h1" | "h2" | "h3" | "p" | "ns";

export type Sentence = {
  id: number,
  text: string,
  translation: string,
  image: string | null,
  format_level: FormatLevel,
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

type GenericTrial = {
  correct: boolean,
  easiness: number,
}

type GenericCardDescriptor<T extends GenericTrial> = {
  lemma_id: number,
  due_date: Date,
  last_trial: null | T,
}

export type CommonCardDescriptor = GenericCardDescriptor<GenericTrial>;

export type TrialType = "ct" | "cc" | "cz" | "show";

export type Trial = GenericTrial & {
  trial_type: TrialType,
}

export type CardDescriptor = GenericCardDescriptor<Trial>

export type MetadataTrial = GenericTrial & {
  metadata_field: string,
}

export type MetadataCardDescriptor = GenericCardDescriptor<MetadataTrial>;

export type MetadataPlaySummary = {
  playing_metadata: MetadataCardDescriptor[],
  not_playable: number,
  unannotated: number,
}

export const EASINESS_DAYS = [
  0,
  1,
  2,
  4,
  10,
  30,
  90,
  365,
];

export type DailySummary = {
  date: Date,
  new_lemmas: number,
  new_lemma_trials: number,
  review_trials: number,
  seconds_taken: number,
}
