import React, {Component} from "react";

import {Lemma, WordInSentence} from "../models";


type Props = {
    word_in_sentence: WordInSentence,
    close: () => void,
}

type State = {
    lemma?: Lemma,
}

export default class LemmaDisplayCard extends Component<Props, State> {
    constructor(props: Props) {
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
                <div className="citation-form">
                    <a href={`/admin/spaced_repetition/lemma/${lemma.id}/change/`} target="_blank">
                        {lemma.citation_form}
                    </a>
                </div>
                <div className="translation">"{lemma.translation}"</div>
            </>;
        }

        return (
            <div className="lemma-card">
                <div className="close" onClick={() => this.props.close()}>X</div>
                <div className="lemma">
                    {content}
                </div>
            </div>
        );
    }
}
