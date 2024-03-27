import React, { Component } from "react";
import { useParams } from "react-router-dom";
const classNames = require('classnames');
import {Sentence, WordInSentence, Substring} from "./models";


const FAKE_WORD_ID = -1;
const UNASSIGNED_LEMMA_ID = -1;
const ASSIGNING_LEMMA_ID = -2;
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
    fetched_words: WordInSentence[],
    assigning_substrings: Substring[],
    selection_start_substring?: number,
    focused?: {
        word_index: number,
        expanded: boolean,
    },
}

class DocumentSentence extends Component<DocumentSentenceProps, DocumentSentenceState> {
    constructor(props: DocumentSentenceProps) {
        super(props);
        this.state = {
            fetched_words: [],
            assigning_substrings: [],
        };
    }

    componentDidMount() {
        fetch(`/api/words_in_sentence?sentence_id=${this.props.sentence.id}`)
            .then(res => res.json())
            .then(words => this.setState({
                fetched_words: words,
                assigning_substrings: [],
                focused: undefined,
            }));
    }

    deriveWordsAndSubstrings(): [WordInSentence[], AssignedSubstring[]] {
        const { text } = this.props.sentence;
        const { fetched_words, assigning_substrings, focused } = this.state;

        const words: WordInSentence[] = [];
        words.push(...fetched_words);

        if (assigning_substrings.length > 0) {
            words.push({
                id: FAKE_WORD_ID,
                sentence_id: this.props.sentence.id,
                lemma_id: ASSIGNING_LEMMA_ID,
                substrings: assigning_substrings,
            });
        }

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
                    id: FAKE_WORD_ID,
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

        return [words, substrings];
    }

    render() {
        const { text } = this.props.sentence;
        const { focused } = this.state;
        const [words, substrings] = this.deriveWordsAndSubstrings();

        const paragraphChildren = substrings.map((assigned_substring, i) => {
            const substring_text = text.substring(assigned_substring.substring.start, assigned_substring.substring.end);
            const substring_focused = focused?.word_index === assigned_substring.word_index;
            const substring_expanded = substring_focused && !!focused?.expanded;

            const {word_index} = assigned_substring;

            if (word_index === undefined) {
                return substring_text;
            } else {
                const onMouseEnter = () => this.setState({focused: {word_index, expanded: false}});
                const onMouseLeave = () => this.setState({focused: undefined});
                const onMouseDown = () => this.setState({selection_start_substring: i});
                const onMouseUp = () => {
                    const selection_object = window.getSelection();

                    if (this.state.selection_start_substring !== undefined && selection_object !== null) {
                        const start = substrings[this.state.selection_start_substring].substring.start + selection_object.anchorOffset;
                        const end = assigned_substring.substring.start + selection_object.focusOffset;

                        if (start !== end) {
                            this.setState({
                                assigning_substrings: this.state.assigning_substrings.concat([{start, end}]),
                                focused: {
                                    word_index: this.state.fetched_words.length, // assigning word index
                                    expanded: false,
                                },
                            });
                            return;
                        }
                    }

                    this.setState({focused: {word_index, expanded: !substring_expanded}});
                }

                const extra_classnames = {
                    sentence_word: true,
                    focused: substring_focused,
                    expanded: substring_expanded,
                };

                const props = {
                    key: i,
                    onMouseEnter,
                    onMouseLeave,
                    onMouseDown,
                    onMouseUp,
                }

                switch (words[word_index].lemma_id) {
                    case UNASSIGNED_LEMMA_ID:
                        return (
                            <span
                                className={classNames('unassigned_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                            </span>
                        );
                    case ASSIGNING_LEMMA_ID:
                        return (
                            <span
                                className={classNames('assigning_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                            </span>
                        );
                    default:
                        return (
                            <span
                                className={classNames('assigned_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                            </span>
                        );
                }
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
