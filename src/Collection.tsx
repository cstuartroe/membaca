import React, { Component } from "react";
import {Link, useParams} from "react-router-dom";
import {Document, Language} from "./models";

type Props = {
    collection_id: number,
}

type State = {
    documents?: Document[],
}


class _Collection extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        this.fetchDocuments()
    }

    fetchDocuments() {
        fetch(`/api/documents?collection_id=${this.props.collection_id}`)
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

export default function Collection(props: {}) {
    const { collectionId } = useParams();

    if (collectionId === undefined) {
        return null;
    }

    return <_Collection collection_id={parseInt(collectionId)}/>
}
