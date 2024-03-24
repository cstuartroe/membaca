import React, { Component } from "react";
import {Link, useParams} from "react-router-dom";
import { Document } from "./models";
import {LoggedInUserState} from "./types";

type Props = {
    user_state: LoggedInUserState,
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
        fetch(`/api/documents?language_id=${this.props.user_state.current_language?.id}`)
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

