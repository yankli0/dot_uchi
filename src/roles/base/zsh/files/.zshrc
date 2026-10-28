# Shared terminal interface on workstation and server.
bindkey -v
bindkey "\e[A" history-beginning-search-backward
bindkey "\e[B" history-beginning-search-forward

_set_terminal_title() { print -Pn "\e]2;%-3~\a" }
precmd_functions+=(_set_terminal_title)

if [[ $SHLVL -le 1 ]] && command -v fastfetch >/dev/null 2>&1; then
  fastfetch
fi

export PATH="$HOME/.local/bin:$PATH"
if command -v mise >/dev/null 2>&1; then
  eval "$(mise activate zsh)"
fi
if command -v zoxide >/dev/null 2>&1; then
  eval "$(zoxide init zsh --cmd cd)"
fi

autoload -Uz compinit
compinit

if [[ -r /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh ]]; then
  source /usr/share/zsh-autosuggestions/zsh-autosuggestions.zsh
fi
if [[ -r /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]]; then
  source /usr/share/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh
fi

alias o="xdg-open"
alias g="git"
alias grep="grep --color=auto"
alias diff="diff --color=auto"
alias ip="ip -c=auto"
alias mv="mv -i"

if command -v eza >/dev/null 2>&1; then
  alias ls="eza"
  alias l="eza"
  alias ll="eza -l"
  alias la="eza -lA"
else
  alias l="ls"
  alias ll="ls -l"
  alias la="ls -lA"
fi

HISTSIZE=100000
SAVEHIST=100000
HISTFILE=~/.history

if command -v nvim >/dev/null 2>&1; then
  export EDITOR="nvim"
else
  export EDITOR="vim"
fi
export VISUAL="$EDITOR"
alias v="$EDITOR"

if command -v starship >/dev/null 2>&1; then
  eval "$(starship init zsh)"
fi
