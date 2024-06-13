import React, {Component} from "react";
import classNames from "classnames";

import {safePost} from "../ajax_utils";
import {Language, Lemma, WordInSentence} from "../models";


export const UNASSIGNED_LEMMA_ID = -1;

type Props = {
    search_string: string,
    language: Language,
    word_in_sentence: WordInSentence,
    loadSentence: () => void,
    close: () => void,
}

type SearchResult = {
    lemma: Lemma,
    exact_match: boolean,
}

type State = {
    suggestions: SearchResult[],
    search_string: string,
    new_lemma?: Lemma,
    status: "unsubmitted" | "submitting" | "submitted",
}

export default class LemmaAssignmentCard extends Component<Props, State> {
    constructor(props: Props) {
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

    componentDidUpdate(prevProps: Readonly<Props>, prevState: Readonly<State>, snapshot?: any) {
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
                    <div className="close" onClick={() => this.props.close()}>X</div>
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
                <div className="close" onClick={() => this.props.close()}><div>X</div></div>
                <div className="button"
                     style={{marginBottom: "5px"}}
                     onClick={() => this.setState({
                         new_lemma: {
                             id: UNASSIGNED_LEMMA_ID,
                             language_id: this.props.language.id,
                             citation_form: this.state.search_string,
                             translation: "",
                             metadata: {},
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
                {this.state.suggestions.map((result, i) => (
                    <div
                        key={i}
                        className={classNames("lemma", "lemma-suggestion", {"exact-match": result.exact_match})}
                        style={{cursor: "pointer"}}
                        onClick={() => this.submitLemma({lemma_id: result.lemma.id})}
                    >
                        <div className="citation-form">{result.lemma.citation_form}</div>
                        <div className="translation">"{result.lemma.translation}"</div>
                    </div>
                ))}
            </div>
        );
    }
}
