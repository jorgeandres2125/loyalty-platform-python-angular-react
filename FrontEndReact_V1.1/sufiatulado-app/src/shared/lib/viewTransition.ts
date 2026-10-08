type NavigateFn = () => void;

export function navigateWithTransition(navigateFn: NavigateFn): void {
  if ('startViewTransition' in document) {
    document.startViewTransition(navigateFn);
  } else {
    navigateFn();
  }
}
