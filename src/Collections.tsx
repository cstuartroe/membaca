import React, { Component } from "react";
import {Link} from "react-router-dom";
import {Collection, Language} from "./models";

type Props = {
    language: Language,
}

type State = {
    collections?: Collection[],
}

export default class Collections extends Component<Props, State> {
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
        fetch(`/api/collections?language_id=${this.props.language.id}`)
            .then(res => res.json())
            .then(data => this.setState({
                collections: data,
            }))
    }

    render() {
        const { collections } = this.state;

        if (collections === undefined) {
            return "Loading...."
        }

        return (
            <div className="col-12">
                {collections.map(collection => (
                    <Link to={`/collection/${collection.id}`} key={collection.id}>
                        <h2>{collection.title}</h2>
                    </Link>
                ))}
            </div>
        );
    }
}

