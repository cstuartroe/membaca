import React, { Component } from "react";
import { useParams } from "react-router-dom";
import {Sentence} from "./models";

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
                        <div className="col-6">
                            {sentence.text}
                        </div>
                        <div className="col-6">
                            {sentence.translation}
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
