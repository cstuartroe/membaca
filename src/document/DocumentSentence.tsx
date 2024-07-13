import React, {Component} from "react";
import {faCheck, faEllipsis} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import classNames from "classnames";

import {safePost} from "../ajax_utils";
import {Language, Sentence, Substring, WordInSentence} from "../models";
import LemmaDisplayCard from "./LemmaDisplayCard";
import LemmaAssignmentCard, {UNASSIGNED_LEMMA_ID} from "./LemmaAssignmentCard";
import LemmaSearchCache from "./LemmaSearchCache";


const FAKE_WORD_ID = -1;
const ASSIGNING_LEMMA_ID = -2;
const SKIP_CHARACTERS: string[] = [
    " ", ".", ",", "!", "?", "\"", "'", ";", "-", "(", ")", "/", ":", "*",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "«", "»",
];


type Props = {
    sentence: Sentence,
    language: Language,
    expand_first_unassigned: boolean,
    mark_fully_assigned: () => void,
}

type AssignedSubstring = {
    substring: Substring,
    word_index?: number,
}

type State = {
    added: boolean,
    fetched_words?: WordInSentence[],
    assigning_substrings: Substring[],
    selection_start_substring?: number,

    lemma_search_cache: LemmaSearchCache,

    // undefined if it has not been set since the sentence was loaded, so first unassigned may be expanded
    // null if a popover was just closed, so that definitely no word is expanded
    expanded_word_index: number | undefined | null,
}

export default class DocumentSentence extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            added: false,
            assigning_substrings: [],
            expanded_word_index: undefined,
            lemma_search_cache: new LemmaSearchCache(props.language.id),
        };
    }

    loadSentence() {
        fetch(`/api/sentence/${this.props.sentence.id}`)
            .then(res => res.json())
            .then(data => {
                this.setState(
                    {
                        added: data.added,
                        fetched_words: data.words,
                        assigning_substrings: [],
                        expanded_word_index: undefined,
                    },
                    () => {
                        const [_, any_unassigned] = this.substringElements();
                        if (!any_unassigned) {
                            this.props.mark_fully_assigned();
                        }
                    }
                )
            })
    }

    add() {
        safePost(
            "/api/sentence_add",
            {sentence_id: this.props.sentence.id},
        )
            .then(() => this.loadSentence());
    }

    componentDidMount() {
        this.loadSentence()
    }

    deriveWordsAndSubstrings(): [WordInSentence[], AssignedSubstring[]] {
        const { text } = this.props.sentence;
        const { fetched_words, assigning_substrings } = this.state;

        const words: WordInSentence[] = [];
        words.push(...fetched_words!);

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

    substringElements(): [React.ReactNode[], boolean] {
        const { language, expand_first_unassigned } = this.props;
        const { text } = this.props.sentence;
        const { expanded_word_index, fetched_words } = this.state;

        const getWordString = (word: WordInSentence) => word.substrings.map(substring => (
            text.substring(substring.start, substring.end)
        )).join(' ');

        if (fetched_words === undefined) {
            return [[text], true];
        }

        const [words, substrings] = this.deriveWordsAndSubstrings();
        if (this.props.expand_first_unassigned) {
            words.forEach(word => this.state.lemma_search_cache.search(getWordString(word)));
        }

        let any_unassigned = false;

        const close = () => this.setState({
            expanded_word_index: null,
        })

        const elements = substrings.map((assigned_substring, i) => {
            const substring_text = text.substring(assigned_substring.substring.start, assigned_substring.substring.end);
            let substring_expanded = expanded_word_index === assigned_substring.word_index;

            const {word_index} = assigned_substring;

            if (word_index === undefined) {
                return substring_text;
            } else {
                const onMouseDown = () => this.setState({selection_start_substring: i});
                const onMouseUp = () => {
                    const selection_object = window.getSelection();
                    if (this.state.selection_start_substring !== undefined && selection_object !== null) {
                        const start = substrings[this.state.selection_start_substring].substring.start + selection_object.anchorOffset;
                        const end = assigned_substring.substring.start + selection_object.focusOffset;

                        if (start !== end) {
                            this.setState({
                                assigning_substrings: this.state.assigning_substrings.concat([{start, end}]),
                                expanded_word_index: fetched_words.length, // assigning substring index
                            });
                            return;
                        }
                    }

                    if (!substring_expanded) {
                        this.setState({
                            expanded_word_index: word_index,
                        })
                    }
                }

                const actually_expand = () => substring_expanded && (assigned_substring.substring === words[word_index].substrings[0]);
                const search_string = getWordString(words[word_index]);

                const extra_classnames = () => ({
                    sentence_word: true,
                    expanded: substring_expanded,
                });

                const props = {
                    onMouseDown,
                    onMouseUp,
                }

                const getWordAndAssignmentCard = (className: string) => {
                    substring_expanded = substring_expanded || (expanded_word_index === undefined && !any_unassigned && expand_first_unassigned);
                    any_unassigned = true;

                    return (
                        <span
                            className={classNames(className, extra_classnames())}
                            key={i}
                        >
                            <span {...props}>{substring_text}</span>
                            {actually_expand() && (
                                <LemmaAssignmentCard
                                    search_string={search_string}
                                    language={language}
                                    loadSentence={() => this.loadSentence()}
                                    word_in_sentence={words[word_index]}
                                    close={close}
                                    lemma_search_cache={this.state.lemma_search_cache}
                                />
                            )}
                        </span>
                    );
                };

                switch (words[word_index].lemma_id) {
                    case UNASSIGNED_LEMMA_ID:
                        return getWordAndAssignmentCard('unassigned_word')

                    case ASSIGNING_LEMMA_ID:
                        return getWordAndAssignmentCard('assigning_word');

                    default:
                        const className = classNames('assigned_word', extra_classnames());

                        if (actually_expand()) {
                            return (
                                <span className={className} key={i} {...props}>
                                    <a
                                        href={`/admin/spaced_repetition/wordinsentence/${words[word_index].id}/change/`}
                                        target="_blank"
                                    >
                                        {substring_text}
                                    </a>
                                    {actually_expand() && (
                                        <LemmaDisplayCard
                                            word_in_sentence={words[word_index]}
                                            close={close}
                                            loadSentence={() => this.loadSentence()}/>
                                    )}
                                </span>
                            );
                        } else {
                            return (
                                <span className={className} key={i} {...props}>
                                    {substring_text}
                                </span>
                            );
                        }
                }
            }
        });

        return [elements, any_unassigned];
    }

    checkBox(ready: boolean) {
        let element: React.ReactNode;
        if (this.state.added) {
            element = <FontAwesomeIcon icon={faCheck}/>;
        } else if (!ready) {
            element = <FontAwesomeIcon icon={faEllipsis}/>;
        } else {
            element = <input
                type="checkbox"
                onClick={() => this.add()}
            />;
        }

        return (
            <a href={`/admin/spaced_repetition/sentence/${this.props.sentence.id}/change/`} target="_blank">
                <div className="sentence-checkbox">
                    {element}
                </div>
            </a>
        );
    }

    render() {
        const [substring_elements, any_unassigned] = this.substringElements();

        return <div className={`document-sentence format-level-${this.props.sentence.format_level}`}>
            {this.checkBox(!any_unassigned)}
            {substring_elements}
        </div>;
    }
}
