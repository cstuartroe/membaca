import React, { Component } from "react";
import { useParams } from "react-router-dom";

import {Sentence, Language} from "../models";
import DocumentSentence from "./DocumentSentence";


type Props = {
    documentId: number,
    language: Language,
}

type State = {
    title?: string,
    link?: string,
    sentences?: Sentence[],
    sentence_indices_marked_fully_assigned: Set<number>,
    num_lemmas_added: number,
}

class _Document extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            sentence_indices_marked_fully_assigned: new Set<number>(),
            num_lemmas_added: 0,
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

    firstNumberNotFullyAssigned() {
        let i = 0;
        while (true) {
            if (!this.state.sentence_indices_marked_fully_assigned.has(i)) {
                return i;
            }
            i++;
        }
    }

    render() {
        const { title, link, sentences } = this.state;
        const first_not_fully_assigned = this.firstNumberNotFullyAssigned();

        return (
            <div className="col-12" style={{paddingBottom: "40vh"}}>
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
                            <DocumentSentence
                                sentence={sentence}
                                language={this.props.language}
                                expand_first_unassigned={i == first_not_fully_assigned}
                                mark_fully_assigned={() => {
                                    this.state.sentence_indices_marked_fully_assigned.add(i)
                                    this.setState({
                                        sentence_indices_marked_fully_assigned: this.state.sentence_indices_marked_fully_assigned,
                                    });
                                }}
                                add_lemmas={n => this.setState({
                                    num_lemmas_added: this.state.num_lemmas_added + n,
                                })}
                            />
                        </div>
                        <div className="col-6 col-md-4">
                            <div className={`document-translation format-level-${sentence.format_level}`}>
                                {sentence.translation}
                            </div>
                        </div>
                    </div>
                ))}

                {this.state.num_lemmas_added > 0 && (
                    <div className="num-lemmas-added">
                        +{this.state.num_lemmas_added} lemmas
                    </div>
                )}
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
