declare namespace JSX {
  interface IntrinsicElements {
    'gmp-place-search': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      orientation?: string;
      selectable?: boolean;
    };
    'gmp-place-all-content': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    'gmp-place-text-search-request': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
    'gmp-place-details-compact': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
      orientation?: string;
    };
    'gmp-place-details-place-request': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement>;
  }
}