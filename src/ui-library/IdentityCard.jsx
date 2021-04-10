import './IdentityCard.scss';
import React from 'react';

import ArtistIllustration from 'svg/artist.svg';
import ListenerIllustration from 'svg/listener.svg';

export default function IdentityCard({ identity, active, onClick, children }) {
    return (
        <div className={`identity-card flex-col nowrap align-center ${active ? 'active' : ''}`} onClick={onClick(identity)}>
            {identity === 'artist' && <ArtistIllustration/>}
            {identity === 'listener' && <ListenerIllustration/>}
            {children}
        </div>
    );
};
