import React, { Component } from "react";
import { useParams } from "react-router-dom";
import {Sentence, WordInSentence, Substring} from "./models";


const UNASSIGNED_LEMMA_ID = -1;
const SKIP_CHARACTERS: string[] = [
    " ",
    ".",
    ",",
    "!",
    "?",
    "\"",
];


type DocumentSentenceProps = {
    sentence: Sentence,
}

type AssignedSubstring = {
    substring: Substring,
    word_index?: number,
}

type DocumentSentenceState = {
    words: WordInSentence[],
    substrings: AssignedSubstring[]
    focused?: {
        word_index: number,
        expanded: boolean,
    },
}

class DocumentSentence extends Component<DocumentSentenceProps, DocumentSentenceState> {
    constructor(props: DocumentSentenceProps) {
        super(props);
        this.state = {
            words: [],
            substrings: [],
        };
    }

    componentDidMount() {
        fetch(`/api/words_in_sentence?sentence_id=${this.props.sentence.id}`)
            .then(res => res.json())
            .then(words => this.setUpWords(words));
    }

    setUpWords(fetched_words: WordInSentence[]) {
        const { text } = this.props.sentence;

        const words: WordInSentence[] = [];
        words.push(...fetched_words);

        const character_assignments: {[key: number]: number | undefined} = {};
        const substrings: AssignedSubstring[] = [];

        words.forEach((word, word_index) => {
            word.substrings.forEach(substring => {
                if (substring.end <= substring.start) {
                    throw `Malformed substring: ${words}`;
                } else if (substring.end > text.length) {
                    throw `Substring past end of sentence`;
                }

                for (let i = substring.start; i < substring.end; i++) {
                    if (character_assignments[i] !== undefined) {
                        throw `Character is assigned to multiple substrings: ${words}`;
                    }
                    character_assignments[i] = word_index;
                }
                substrings.push({
                    substring,
                    word_index,
                })
            });
        });

        type State = "assigned_word" | "unassigned_word" | "skip_characters" | "begin"
        let state: State = "begin";
        let currentTokenStart = -1;

        const addUnassignedSubstring = (state: State, end: number) => {
            const substring: Substring = {
                start: currentTokenStart,
                end,
            }

            if (state === "unassigned_word") {
                substrings.push({
                    substring,
                    word_index: words.length,
                })
                words.push({
                    id: -1,
                    sentence_id: this.props.sentence.id,
                    lemma_id: UNASSIGNED_LEMMA_ID,
                    substrings: [
                        substring,
                    ],
                })
            } else if (state === "skip_characters") {
                substrings.push({
                    substring,
                })
            }
            // else, do nothing
        }

        for (let i = 0; i < text.length; i++) {
            const initialState: State = state;

            if (character_assignments[i] !== undefined) {
                state = "assigned_word";
            } else if (SKIP_CHARACTERS.includes(text[i])) {
                state = "skip_characters";
            } else {
                state = "unassigned_word";
            }

            if (initialState != state) {
                addUnassignedSubstring(initialState, i);
                currentTokenStart = i;
            }
        }
        addUnassignedSubstring(state, text.length);

        substrings.sort((a, b) => a.substring.start - b.substring.start);

        this.setState({words, substrings, focused: undefined});
    }

    render() {
        const { text } = this.props.sentence;
        const { words, substrings } = this.state;

        const paragraphChildren = this.state.substrings.map(assigned_substring => {
            const substring_text = text.substring(assigned_substring.substring.start, assigned_substring.substring.end);
            if (assigned_substring.word_index === undefined) {
                return substring_text;
            } else if (words[assigned_substring.word_index].id === UNASSIGNED_LEMMA_ID) {
                return <span style={{backgroundColor: "#999"}}>{substring_text}</span>;
            } else {
                return <span style={{backgroundColor: "#9f9"}}>{substring_text}</span>;
            }
        });

        return <p>{paragraphChildren}</p>;
    }
}


type Props = {
    documentId: number,
}

type State = {
    title?: string,
    link?: string,
    sentences?: Sentence[],
}

class _Document extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        fetch(`/api/document/${this.props.documentId}`)
            .then(res => res.json())
            .then(data => this.setState({
                title: data["title"],
                link: data["link"],
                sentences: data["sentences"],
            }))
    }

    render() {
        const { title, link, sentences } = this.state;

        return (
            <div className="col-12">
                <a href={link}>
                    <h2>{title}</h2>
                </a>
                {sentences?.map((sentence, i) => (
                    <div className="row" key={i} style={{paddingBottom: ".5vh"}}>
                        <div className="col-6 col-md-4 offset-md-2">
                            <DocumentSentence sentence={sentence}/>
                        </div>
                        <div className="col-6 col-md-4">
                            <p>{sentence.translation}</p>
                        </div>
                    </div>
                ))}
            </div>
        );
    }
}

export default function Document(props: {}) {
    const { documentId } = useParams();

    if (documentId === undefined) {
        return null;
    }

    return <_Document documentId={parseInt(documentId)}/>
}
