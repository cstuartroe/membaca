import React, { Component } from "react";
import {Link} from "react-router-dom";
import {CardDescriptor, Language} from "./models";

type Props = {
    is_superuser: boolean,
    current_language: Language,
}

type State = {
    card_descriptors?: CardDescriptor[],
}

export default class Dashboard extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
        };
    }

    componentDidMount() {
        fetch(`/api/playing_lemmas?language_id=${this.props.current_language.id}`)
            .then(res => res.json())
            .then(data => this.setState({card_descriptors: data.map((descriptor: any) => ({
                    ...descriptor,
                    due_date: new Date(descriptor.due_date),
                }))}))
    }


    render() {
        const { card_descriptors } = this.state;

        if (card_descriptors === undefined) {
            return null;
        }

        const new_cards = card_descriptors.filter(card => card.last_trial === null)
        const seen_cards = card_descriptors.filter(card => card.last_trial !== null)
        const now = new Date();
        const due_cards = seen_cards.filter(card => card.due_date < now);

        return (
            <div className="col-12 col-md-6 offset-md-3">
                <div className="row">
                    <div className="col-12">
                        <p>
                            {seen_cards.length}/{card_descriptors.length} cards playing.
                            {' '}{due_cards.length} cards ready for review.
                        </p>
                    </div>
                    <div className="col-6">
                        <Link to="/cards/review">
                            <div className="big button">
                                Review cards
                            </div>
                        </Link>
                    </div>
                    <div className="col-6">
                        <Link to="/cards/new">
                            <div className="big button">
                                Learn new cards
                            </div>
                        </Link>
                    </div>
                    <div className="col-12">
                        <p>
                            domcumints
                        </p>
                    </div>
                    <div className="col-6">
                        <Link to="/documents">
                            <div className="big button">
                                See documents
                            </div>
                        </Link>
                    </div>
                </div>
            </div>
        );
    }
}
