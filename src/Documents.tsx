import React, { Component } from "react";
import {Link} from "react-router-dom";
import {Document, Language} from "./models";

type Props = {
    language: Language,
}

type State = {
    documents?: Document[],
}

export default class Documents extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        this.fetchDocuments()
    }

    componentDidUpdate(prevProps: Readonly<Props>, prevState: Readonly<State>, snapshot?: any) {
        if (prevProps.language !== this.props.language) {
            this.fetchDocuments();
        }
    }

    fetchDocuments() {
        fetch(`/api/documents?language_id=${this.props.language.id}`)
            .then(res => res.json())
            .then(data => this.setState({
                documents: data,
            }))
    }

    render() {
        const { documents } = this.state;

        if (documents === undefined) {
            return "Loading...."
        }

        return (
            <div className="col-12">
                {documents.map(document => (
                    <Link to={`/document/${document.id}`} key={document.id}>
                        <h2>{document.title}</h2>
                    </Link>
                ))}
            </div>
        );
    }
}

