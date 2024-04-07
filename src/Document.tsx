import React, { Component } from "react";
import { useParams } from "react-router-dom";
const classNames = require('classnames');
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import { faCheck, faEllipsis } from "@fortawesome/free-solid-svg-icons";
import {Sentence, WordInSentence, Substring, Lemma, Language} from "./models";
import {safePost} from "./ajax_utils";


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
    "'",
    ";",
    "-",
    "(",
    ")",
    "/",
];


type LemmaDisplayCardProps = {
    word_in_sentence: WordInSentence,
}

type LemmaDisplayCardState = {
    lemma?: Lemma,
}

class LemmaDisplayCard extends Component<LemmaDisplayCardProps, LemmaDisplayCardState> {
    constructor(props: LemmaDisplayCardProps) {
        super(props);
        this.state = {};
    }

    componentDidMount() {
        const { lemma_id } = this.props.word_in_sentence;

        if (lemma_id === null) {
            return;
        }

        fetch(`/api/lemma?id=${lemma_id}`)
            .then(res => res.json())
            .then(lemma => this.setState({lemma}));
    }

    render() {
        const { lemma } = this.state;

        let content: React.ReactNode = null;

        if (this.props.word_in_sentence.lemma_id === null) {
            content = "No lemma"
        } else if (lemma !== undefined) {
            content = <>
                <div className="citation-form">{lemma.citation_form}</div>
                <div className="translation">"{lemma.translation}"</div>
            </>;
        }

        return (
            <div className="lemma-card">
                <div className="lemma">
                    {content}
                </div>
            </div>
        );
    }
}

type LemmaAssignmentCardProps = {
    search_string: string,
    language: Language,
    word_in_sentence: WordInSentence,
    loadSentence: () => void,
}

type LemmaAssignmentCardState = {
    suggestions: Lemma[],
    search_string: string,
    new_lemma?: Lemma,
    status: "unsubmitted" | "submitting" | "submitted",
}

class LemmaAssignmentCard extends Component<LemmaAssignmentCardProps, LemmaAssignmentCardState> {
    constructor(props: LemmaAssignmentCardProps) {
        super(props);
        this.state = {
            suggestions: [],
            search_string: props.search_string,
            status: "unsubmitted",
        }
    }

    performSearch() {
        const search_string = this.state.search_string;

        fetch(`/api/search_lemmas?language_id=${this.props.language.id}&q=${search_string}&num_results=5`)
            .then(res => res.json())
            .then(suggestions => this.setState({suggestions}));
    }

    componentDidMount() {
        this.performSearch()
    }

    componentDidUpdate(prevProps: Readonly<LemmaAssignmentCardProps>, prevState: Readonly<LemmaAssignmentCardState>, snapshot?: any) {
        if (prevState.search_string != this.state.search_string) {
            this.performSearch();
        }
    }

    submitNewLemma() {
        const { new_lemma } = this.state;
        if (new_lemma === undefined) { return; }

        this.submitLemma({
            lemma: {
                citation_form: new_lemma.citation_form,
                translation: new_lemma.translation,
            }
        });
    }

    submitLemma(data: any) {
        this.setState({status: "submitting"});
        safePost(
            "/api/words_in_sentence",
            {
                sentence_id: this.props.word_in_sentence.sentence_id,
                language_id: this.props.language.id,
                substrings: this.props.word_in_sentence.substrings,
                ...data,
            },
        ).then(res => {
            if (res.ok) {
                this.setState({status: "submitted"});
                this.props.loadSentence();
            }
        })
    }

    render() {
        const { new_lemma, status } = this.state;

        if (status === "submitted") {
            return null;
        }

        if (new_lemma !== undefined) {
            return (
                <div className="lemma-card">
                    <div className="label">Citation form</div>
                    <div>
                        <input
                            type="text"
                            value={new_lemma.citation_form}
                            onChange={e => this.setState({
                                new_lemma: {...new_lemma, citation_form: e.target.value},
                            })}/>
                    </div>
                    <div className="label">Translation</div>
                    <div>
                        <input
                            type="text"
                            value={new_lemma.translation}
                            onChange={e => this.setState({
                                new_lemma: {...new_lemma, translation: e.target.value},
                            })}/>
                    </div>
                    <div
                        className="button"
                        style={{marginTop: "5px"}}
                        onClick={() => {
                            if (status === "unsubmitted") {
                                this.submitNewLemma();
                            }
                        }}
                    >
                        {(status === "unsubmitted") ? "Submit" : "..."}
                    </div>
                </div>
            );
        }

        return (
            <div className="lemma-card">
                <div className="button"
                     style={{marginBottom: "5px"}}
                     onClick={() => this.setState({
                         new_lemma: {
                             id: UNASSIGNED_LEMMA_ID,
                             language_id: this.props.language.id,
                             citation_form: this.props.search_string,
                             translation: "",
                         }
                     })}
                >
                    New lemma
                </div>

                <div className="button"
                     style={{marginBottom: "5px"}}
                     onClick={() => this.submitLemma({})}
                >
                    No lemma
                </div>

                <div>
                    <input
                        type="text"
                        value={this.state.search_string}
                        onChange={e => this.setState({
                            search_string: e.target.value,
                        })}/>
                </div>
                {this.state.suggestions.map((lemma, i) => (
                    <div
                        key={i}
                        className="lemma"
                        style={{cursor: "pointer"}}
                        onClick={() => this.submitLemma({lemma_id: lemma.id})}
                    >
                        <div className="citation-form">{lemma.citation_form}</div>
                        <div className="translation">"{lemma.translation}"</div>
                    </div>
                ))}
            </div>
        );
    }
}


type DocumentSentenceProps = {
    sentence: Sentence,
    language: Language,
}

type AssignedSubstring = {
    substring: Substring,
    word_index?: number,
}

type DocumentSentenceState = {
    added: boolean,
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
            added: false,
            fetched_words: [],
            assigning_substrings: [],
        };
    }

    loadSentence() {
        fetch(`/api/sentence/${this.props.sentence.id}`)
            .then(res => res.json())
            .then(data => this.setState({
                added: data.added,
                fetched_words: data.words,
                assigning_substrings: [],
                focused: undefined,
            }));
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

    substringElements(): [React.ReactNode[], boolean] {
        const { language } = this.props;
        const { text } = this.props.sentence;
        const { focused } = this.state;
        const [words, substrings] = this.deriveWordsAndSubstrings();

        let any_unassigned = false;

        const elements = substrings.map((assigned_substring, i) => {
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

                    if (!substring_expanded) {
                        this.setState({focused: {word_index, expanded: true}});
                    }
                }

                const actually_expand = substring_expanded && (assigned_substring.substring === words[word_index].substrings[0]);
                const search_string = words[word_index].substrings.map(substring => (
                    text.substring(substring.start, substring.end))).join(' ');

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
                        any_unassigned = true;
                        return (
                            <span
                                className={classNames('unassigned_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                                {actually_expand && (
                                    <LemmaAssignmentCard
                                        search_string={search_string}
                                        language={language}
                                        loadSentence={() => this.loadSentence()}
                                        word_in_sentence={words[word_index]}
                                    />
                                )}
                            </span>
                        );
                    case ASSIGNING_LEMMA_ID:
                        any_unassigned = true;
                        return (
                            <span
                                className={classNames('assigning_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                                {actually_expand && (
                                    <LemmaAssignmentCard
                                        search_string={search_string}
                                        language={language}
                                        loadSentence={() => this.loadSentence()}
                                        word_in_sentence={words[word_index]}
                                    />
                                )}
                            </span>
                        );
                    default:
                        return (
                            <span
                                className={classNames('assigned_word', extra_classnames)}
                                {...props}
                            >
                                {substring_text}
                                {actually_expand && (
                                    <LemmaDisplayCard word_in_sentence={words[word_index]}/>
                                )}
                            </span>
                        );
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

        return <div className="sentence-checkbox">
            {element}
        </div>;
    }

    render() {
        const [substring_elements, any_unassigned] = this.substringElements();

        return <div className="document-sentence">
            {this.checkBox(!any_unassigned)}
            {substring_elements}
        </div>;
    }
}


type Props = {
    documentId: number,
    language: Language,
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
                        {(sentence.image !== null ) ? (
                            <div className="col-12 col-md-8 offset-md-2" style={{display: "flex"}}>
                                <img src={sentence.image} style={{
                                    maxWidth: "100%",
                                    maxHeight: "30vh",
                                    margin: "auto",
                                    padding: "10px 0",
                                }}/>
                            </div>
                        ) : null}
                        <div className="col-6 col-md-4 offset-md-2">
                            <DocumentSentence sentence={sentence} language={this.props.language}/>
                        </div>
                        <div className="col-6 col-md-4">
                            <div className="document-translation">{sentence.translation}</div>
                        </div>
                    </div>
                ))}
            </div>
        );
    }
}

export default function Document(props: {language: Language}) {
    const { documentId } = useParams();

    if (documentId === undefined) {
        return null;
    }

    return <_Document documentId={parseInt(documentId)} language={props.language}/>
}
